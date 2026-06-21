# Payments Team Playbook

> _Last updated: 2025-11-20 · Owner: Payments Team_

Team-specific norms for engineers working on the Payments services
(Authorization, Capture, Payouts).

## Standups

Daily at 10:00 Berlin time. Async update in **#team-payments** if you can't join.

## Pull requests on our services

- For **non-critical services** (internal tooling, dashboards, docs), **1
  approval** is enough to merge — we optimize for speed on low-risk changes.
- For anything touching money movement (Authorization, Capture, Payouts), follow
  the standard review rules.

## Running the test suite

- Unit tests run in **GitHub Actions** on every PR.
- Our nightly load tests still run in **Jenkins** — see the `payments-nightly`
  job. If a nightly fails, the on-call engineer triages it the next morning.

## Local setup quirks

The Payments services need a seeded test database. Run `make seed-db` after
`docker compose up`, or the integration tests will fail with "no merchants
found".
