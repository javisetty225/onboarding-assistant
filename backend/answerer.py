"""Generate a grounded, conflict-aware answer from retrieved chunks."""

import json
import time

from . import config
from .prompts import SYSTEM_PROMPT, build_user_message
from .retriever import retrieve
from .schemas import AskResponse, Citation, ConflictFlag


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def _safe(model, d):
    try:
        return model(**d)
    except Exception:
        return None


def _parse(raw: str) -> AskResponse:
    data = json.loads(_strip_fences(raw))
    # Build defensively: one malformed citation/conflict shouldn't discard the
    # whole structured answer.
    citations = [c for c in (_safe(Citation, x) for x in data.get("citations", [])) if c]
    conflicts = [c for c in (_safe(ConflictFlag, x) for x in data.get("conflicts", [])) if c]
    return AskResponse(
        answer=data.get("answer", "").strip(),
        confidence=data.get("confidence", "medium"),
        citations=citations,
        conflicts=conflicts,
    )


def _ground_citations(citations: list[Citation], chunks) -> list[Citation]:
    """Replace model-asserted citation metadata with ground truth from the
    retrieved chunks, and drop any citation to a doc we never actually fetched
    (i.e. a hallucinated source). The whole pitch is trust — the receipts must
    be real, not the model's recollection."""
    by_doc: dict[str, object] = {}
    for c in chunks:
        by_doc.setdefault(c.doc, c)  # keep the closest-matching chunk per doc

    grounded: list[Citation] = []
    for cit in citations:
        src = by_doc.get(cit.doc)
        if src is None:
            continue  # not in the retrieved set -> don't vouch for it
        cit.owner = None if src.owner == "unknown" else src.owner
        cit.last_updated = None if src.last_updated == "unknown" else src.last_updated
        grounded.append(cit)
    return grounded


def _date_key(c) -> str:
    # Treat an unknown date as the oldest possible, so it never wins on recency.
    return c.last_updated if c.last_updated and c.last_updated != "unknown" else "0000-00-00"


def _fallback(chunks) -> AskResponse:
    # No API key: return the highest-authority, most-recent chunk so the
    # pipeline is still demonstrable end to end.
    if not chunks:
        return AskResponse(
            answer="I couldn't find anything about that in the docs. Try #eng-help.",
            confidence="low",
        )
    ranked = sorted(chunks, key=_date_key, reverse=True)
    ranked.sort(key=lambda c: c.authority_rank)  # stable: authority first
    best = ranked[0]
    return AskResponse(
        answer=f"(LLM disabled — showing best-matching source)\n\n{best.text}",
        confidence="low",
        citations=[
            Citation(
                doc=best.doc,
                owner=None if best.owner == "unknown" else best.owner,
                last_updated=None if best.last_updated == "unknown" else best.last_updated,
                snippet=best.text[:300],
            )
        ],
    )


def answer(question: str, top_k: int = config.DEFAULT_TOP_K) -> AskResponse:
    start = time.time()
    chunks = retrieve(question, top_k=top_k)

    if not config.ANTHROPIC_API_KEY:
        resp = _fallback(chunks)
    else:
        import anthropic

        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=config.ANSWER_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_message(question, chunks)}],
        )
        raw = "".join(b.text for b in message.content if b.type == "text")
        try:
            resp = _parse(raw)
            resp.citations = _ground_citations(resp.citations, chunks)
        except (json.JSONDecodeError, TypeError, ValueError):
            resp = AskResponse(answer=raw.strip(), confidence="low")

    resp.latency_ms = int((time.time() - start) * 1000)
    return resp