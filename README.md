# Payrails Onboarding Assistant

A conflict-aware Q&A assistant that helps a new engineer get a **reliable** answer
from the onboarding docs in seconds — and, crucially, tells them when the docs
disagree instead of confidently picking the wrong one.

---

## The problem I chose to solve (and what I deliberately didn't)

The brief is "use AI to help new joiners find answers faster." The obvious move is
"build a RAG chatbot over the docs." I think that's the wrong target: plain
semantic search already finds the right pages here — the docs aren't *hard to
find*, they're **contradictory**.

The provided set has four planted conflicts:

| Question | Stale / wrong source | Correct source | Why it wins |
|---|---|---|---|
| Staging access | `02-it-helpdesk-faq.md` (2023) — needs VPN | `01-environments-and-access.md` (2026) — self-serve, no VPN | newer + current platform doc |
| PR approvals | `04-payments-team-playbook.md` — 1 approval for non-critical | `03-code-review-and-prs.md` — 2 min, *teams may not remove* | org-wide rule, explicitly authoritative |
| Fraud Detection owner | `05-service-catalog.md` — Marco Reyes | `06-org-changes-2026.md` — Priya Nair | change log supersedes the catalog |
| Deploy timing | `08-glossary.md` — any time | `07-deploys-releases.md` — Tue/Thu | authority over a *newer* glossary entry |

In a payments company, a confident **wrong** answer ("deploy Friday, one approval
is fine") is worse than no answer. So the thing worth building is **trust**:
answers that are grounded, cited, and that flag disagreement.

Scope is intentionally narrow — one assistant, one job — per the brief's "a
focused solution beats a sprawling AI platform."

---

## How it works

```
question
   │
   ▼
[ retriever ]  semantic search over Chroma (local MiniLM embeddings).
   │           Returns top-k chunks tagged: source · owner · last_updated · authority_rank
   ▼
[ answerer ]  Claude with a conflict-resolution prompt:
   │           1. answer ONLY from retrieved chunks (no hallucination)
   │           2. on disagreement -> resolve by authority, then recency
   │           3. cite sources  4. flag the conflict  5. report confidence
   ▼
[ ground ]    citations are reconciled against the chunks we actually
   │           retrieved: dates/owners are overwritten with ground truth and
   │           any citation to a doc we didn't fetch is dropped (no fake receipts).
   ▼
{ answer, confidence, citations[], conflicts[] }
```

The conflict logic lives in two auditable places:

- **`backend/config.py` -> tiers + `DOC_TIER`** — authority is assigned by
  *document type* (org-rule > platform > reference > catalog/team > legacy), not
  by hand-picked per-file numbers, so a new doc inherits the authority of its
  kind. A doc can also self-declare with an `Authority: <n>` field in its header,
  which means adding a new authoritative source needs **no code change**.
- **`backend/prompts.py` -> `SYSTEM_PROMPT`** — the policy: authority first,
  recency second, always cite, always surface the loser. Confidence drops to
  `medium` when authority has to override a *newer* source (e.g. deploy timing),
  because that's the kind of call a human might reasonably dispute.

Embeddings run locally, so the index builds with **no API key**. Only answer
generation calls Claude; with no key set, the app falls back to retrieval-only so
the pipeline still runs end to end.

---

## Run it

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). Dependencies are
declared in `pyproject.toml` (and pinned in `uv.lock`).

```bash
uv sync                                  # creates .venv and installs from pyproject.toml / uv.lock

# Optional: set your key so answers are generated (not just retrieved).
# Without it the app still runs, in retrieval-only fallback mode.
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

uv run python -m backend.ingest          # builds the vector index from docs/
uv run uvicorn backend.main:app --reload
# open http://localhost:8000   (interactive API docs at /docs)
```

The first question after boot is slow (~15-20s) while the embedding model loads;
warm requests are ~5-8s.

## Measure it

The eval calls the real answerer, so it needs `ANTHROPIC_API_KEY` set — without
it the harness runs in retrieval-only fallback (no conflict resolution) and the
numbers below won't reproduce. It warns you if the key is missing.

```bash
uv run python -m eval.evaluate
```

Current results on the 10-question golden set:

```
Answer correctness : 10/10 (100%)
Safety (no stale)  : 10/10 (100%)
Citation accuracy  : 10/10 (100%)
Conflict recall    : 100%  (caught 6, missed 0)
Conflict precision : 100%  (false alarms 0)
Latency p50/p95    : ~5.8s / ~17s (first run = cold model load)
```

The two metrics I'd put on a dashboard first are **Safety** (never repeat a stale
fact) and **Conflict recall** (never silently pick a side).

> Note on the harness: safety/citation use keyword and phrase matching, which is
> brittle on negation ("you do **not** need a VPN" contains "VPN"). The forbidden
> lists are claim-shaped to avoid that, but the real fix at scale is an
> **LLM-as-judge** — see "What's next".

---

## Project layout

```
backend/      FastAPI app, ingestion, retrieval, conflict-aware answering
frontend/     single-file chat UI (citations + conflict cards)
docs/         the onboarding knowledge base (source of truth)
eval/         golden set + metrics harness
walkthrough/  the presentation narrative
```

## What I'd build next

1. **LLM-as-judge** for the eval — grade whether the answer *asserts* a stale
   claim, instead of string-matching; generalizes to unseen questions.
2. **Feedback loop** — a thumbs up/down per answer feeding the golden set, so "was
   this useful" becomes a measured number.
3. **Auto-conflict detection at ingest** — diff the same fact across docs and open
   a ticket for the doc owner, so the source of truth gets *fixed*, not just
   worked around.
4. **Freshness signals** — warn when an answer rests on a doc older than N months.
5. **Slack front door** — most of these questions are already asked in #eng-help.