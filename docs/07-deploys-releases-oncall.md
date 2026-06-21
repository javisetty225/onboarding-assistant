# Deploys, Releases & On-Call

> _Last updated: 2026-04-10 · Owner: Platform Engineering_

## Deploy schedule

Deploys to production go out on **Tuesdays and Thursdays**. Cut your release by
16:00 Berlin time the day before so it can be reviewed.

> Friday deploys are discouraged. Avoid deploying right before a weekend or a
> public holiday.

## How a deploy works

1. Merge to `main` (squash). GitHub Actions builds and publishes the artifact.
2. Promote the build to staging via the deploy pipeline and verify.
3. Promote to production on the next deploy day.

## On-call

- Each team runs its own weekly on-call rotation, tracked in the on-call tool.
- On-call responds to alerts from **Sentry** (errors) and **Grafana** (metrics
  and dashboards).
- Escalation path: on-call engineer → team lead → Platform on-call → CTO for
  Sev-1 incidents affecting money movement.

## Incidents

- Declare incidents in **#incidents**. Open a doc from the incident template.
- During an active incident there is a **deploy freeze** until the incident is
  resolved and an all-clear is posted.
