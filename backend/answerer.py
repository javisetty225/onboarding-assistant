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


def _parse(raw: str) -> AskResponse:
    data = json.loads(_strip_fences(raw))
    return AskResponse(
        answer=data.get("answer", "").strip(),
        confidence=data.get("confidence", "medium"),
        citations=[Citation(**c) for c in data.get("citations", [])],
        conflicts=[ConflictFlag(**c) for c in data.get("conflicts", [])],
    )


def _fallback(chunks) -> AskResponse:
    # No API key: return the highest-authority, most-recent chunk so the
    # pipeline is still demonstrable end to end.
    if not chunks:
        return AskResponse(
            answer="I couldn't find anything about that in the docs. Try #eng-help.",
            confidence="low",
        )
    ranked = sorted(chunks, key=lambda c: c.last_updated, reverse=True)
    ranked.sort(key=lambda c: c.authority_rank)
    best = ranked[0]
    return AskResponse(
        answer=f"(LLM disabled — showing best-matching source)\n\n{best.text}",
        confidence="low",
        citations=[
            Citation(
                doc=best.doc,
                owner=best.owner,
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
        except (json.JSONDecodeError, TypeError, ValueError):
            resp = AskResponse(answer=raw.strip(), confidence="low")

    resp.latency_ms = int((time.time() - start) * 1000)
    return resp