# Service Catalog & Owners

> _Last updated: 2025-12-15 · Owner: Platform Engineering_

The owning engineer is the default code owner and the first point of contact
for questions about a service.

| Service | Description | Owner |
|---|---|---|
| Authorization | Authorizes incoming payments | Lena Fischer |
| Capture | Captures authorized payments | Lena Fischer |
| Payouts | Pays out to merchants | Tomás Andrade |
| Fraud Detection | Real-time fraud scoring | Marco Reyes |
| PSP Gateway | Routes to Stripe / Adyen / PayPal | Priya Nair |
| Merchant API | Public-facing merchant API | Sofia Kühn |
| Reporting | Merchant dashboards & exports | Daniel Weiss |

> To find the current owner programmatically, each service repo also has a
> `CODEOWNERS` file — but it is not always kept up to date, so treat this table
> as the source of truth.
