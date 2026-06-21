# Glossary & Common Questions

> _Last updated: 2026-05-08 · Owner: Developer Experience_

## Common #eng-help questions

**How do I get access to staging?**
Self-serve through the Access Portal at `https://go/access` — request the
`staging-engineering` role. No VPN needed. (See `01-environments-and-access.md`.)

**Can I deploy whenever I want?**
Yes — you can ship to production **any time** through the deploy pipeline once
your PR is merged and green. We only stop deploys during an active incident
(deploy freeze). There's no fixed deploy day.

**How many approvals does my PR need?**
Two approvals org-wide, including one code owner. (See `03-code-review-and-prs.md`.)

**Who owns the service I'm changing?**
Check the service catalog (`05-service-catalog-and-owners.md`) and the latest
org changes (`06-org-changes-2026.md`).

**What's the difference between staging and pre-prod?**
Nothing — they're the same environment. We're standardizing on "staging".

## Glossary

| Term | Meaning |
|---|---|
| PSP | Payment Service Provider (e.g. Stripe, Adyen, PayPal) |
| Orchestration | Routing a payment across PSPs and modules |
| Capture | Settling a previously authorized payment |
| Payout | Disbursing funds to a merchant |
| Sev-1 | Highest-severity incident; affects money movement |
| Code owner | The engineer/team that must approve changes to a service |
