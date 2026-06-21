# Environments & Getting Access

> _Last updated: 2026-04-30 · Owner: Platform Engineering_

## Our environments

| Environment | Purpose | How to reach it |
|---|---|---|
| `local` | Your machine | docker compose up |
| `staging` | Shared pre-production environment for integration testing | `https://staging.internal.example` |
| `production` | Live merchant traffic | restricted |

> **Note:** Some older docs and a few teams still call `staging` "**pre-prod**".
> They are the same environment. We are standardizing on the name **staging**.

## Getting access to staging

Access is **self-serve** as of 2026. You do **not** need a VPN.

1. Go to the **Access Portal** at `https://go/access`.
2. Sign in with your Okta account (`<your-okta-login>`).
3. Request the **`staging-engineering`** role. Approval is automatic for anyone
   in the Engineering group and usually lands within a few minutes.
4. Once approved, staging is reachable from any company-managed laptop on any
   network — no VPN required.

If the Access Portal shows an error, post in **#eng-help** and tag the
Platform on-call.

## Production access

Production access is granted per-service and requires your team lead's approval
plus a short security training. Don't request it in your first week — you won't
need it.
