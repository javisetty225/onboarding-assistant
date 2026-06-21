# Code Review & Pull Requests

> _Last updated: 2026-05-02 · Owner: Engineering Excellence_

These are the **org-wide** rules for pull requests. Individual teams may add to
them but may not remove them.

## Branching

- Branch off `main`. Name branches `type/short-description`, e.g.
  `feat/add-refund-webhook` or `fix/payout-rounding`.
- Keep PRs small — under ~400 lines of diff where possible.

## Approvals

- Every PR requires a **minimum of 2 approvals** before merge.
- At least one approval must come from a **code owner** of the affected service
  (see `05-service-catalog-and-owners.md`).
- No self-merges, no exceptions.

## CI

- All CI runs on **GitHub Actions**. Required checks: lint, unit tests,
  integration tests, and the security scan.
- The pipeline must be green before merge. Flaky tests should be reported in
  **#eng-help**, not skipped.

## Merging

- We use **squash merge** into `main`.
- The PR title becomes the commit message, so write it like a changelog entry.
