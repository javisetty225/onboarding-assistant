# Walkthrough — Payrails Onboarding Assistant

A slide-by-slide narrative for the ~15 min walkthrough. One idea per slide.
The indented lines are roughly what you say.

---

## Slide 1 — The real problem (not the obvious one)

**Show:** the four-row conflict table.

> "The brief looks like 'build a RAG bot over the docs.' But I read the docs
> first, and the answers aren't hard to *find* — search nails them. The problem is
> the docs **contradict each other**, on purpose. The 2023 IT FAQ says you need a
> VPN for staging; the 2026 doc says it's self-serve. The Payments playbook says
> one approval is fine; the org-wide rule says two and that teams can't override
> it. The catalog says Marco owns Fraud Detection; the change log says it moved to
> Priya in March.
>
> In a payments company, a confident wrong answer is worse than no answer. So the
> thing worth solving isn't search — it's **trust**."

This slide alone hits the top rubric line: *understood the problem before reaching
for a tool.*

---

## Slide 2 — What I built

**Show:** the architecture diagram (retriever -> answerer -> answer object).

> "Small FastAPI service. Retrieval is local embeddings into Chroma, so the index
> builds with no API key. The answer step calls Claude with one job: answer only
> from the retrieved chunks, and when they disagree, resolve by **authority first,
> recency second**, then cite the source and **flag the conflict**.
>
> Every chunk carries its source, owner, and last-updated date, so the model
> reasons over freshness, not just text. The whole conflict policy lives in two
> readable places — an authority-rank dict and the system prompt — so it's
> auditable, not magic."

---

## Slide 3 — Demo (the money moment)

**Live, warm the model first, then ask:** *"How do I get access to staging?"*

> "It says self-serve, no VPN. Below it, a **'Sources disagree'** card naming the
> 2023 IT FAQ and why it lost: older and lower authority. Then the source ledger
> with the exact file and date. The new joiner gets the right answer *and* the
> receipt, in one screen."

**Then ask:** *"When can I deploy to production?"* — this is the strongest case.

> "Notice this one comes back **medium** confidence, not high. The glossary is
> actually the *newer* doc and says 'deploy any time' — a naive 'newest wins'
> system would tell the new engineer exactly the wrong thing. Mine trusts the
> deploy doc because authority outranks recency, but it *lowers confidence* and
> flags it, because that's a call a human might dispute. That contrast — high when
> sources agree, medium when authority overrides recency — is the behaviour I'm
> most proud of."

---

## Slide 4 — The working session (when requirements shift)

Be ready for the curveballs:

- **"A doc has no date."** -> metadata falls back to `unknown`; authority rank
  still breaks the tie; confidence drops.
- **"A new conflicting doc appears."** -> it's a file in `docs/`; re-run ingest. If
  authoritative, add one line to `AUTHORITY_RANK`. No logic change.
- **"It answered something not in the docs."** -> the prompt forbids that; it's
  told to say "not in the docs, ask #eng-help."
- **"Why not just fix the docs?"** -> that's the next step (auto-detect conflicts,
  file a ticket to the owner). The assistant is the stopgap *and* the detector.

---

## Slide 5 — How I'd know it's working

**Show:** the `eval/evaluate.py` output (10/10 across the board).

> "I wrote a 10-question golden set with the *resolved* answers and track five
> things. The two that matter most: **Safety** — does it ever repeat a stale fact
> like 'VPN' or 'Marco'? — and **Conflict recall** — of the real conflicts, how
> many did it flag? Both 100%.
>
> Honest bit: my first safety check was a naive keyword match and it produced
> false positives — 'you do *not* need a VPN' contains the word 'VPN'. I tightened
> it to match the actual stale *claim*. But that's still brittle, so the real next
> step is an **LLM-as-judge** that grades meaning, not strings. You can see that
> iteration in the commit history."

This is the slide that shows you measure impact, not just ship tech — and that you
critique your own work.

---

## Slide 6 — Honest limits & what's next

> "It's a prototype. Embeddings are a small local model — fine for nine docs, I'd
> revisit at scale. The authority ranking is hand-curated — deliberate for
> auditability, a cost at scale. Next, in order: LLM-as-judge for the eval, a
> thumbs up/down feedback loop, auto-conflict detection that files a ticket to fix
> the doc, freshness warnings, and a Slack front door since that's where people
> already ask."

---

## The one sentence to land

> "I didn't build a chatbot over the docs — I built the thing that makes a new
> joiner *trust* the answer: grounded, cited, and honest when the docs disagree."
