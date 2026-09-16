# API contract index (reference only)

This index is a deliberately broad distractor. None of these endpoints is used
by the CTX-01 validator, and this file must remain unchanged by a model patch.

| endpoint | method | idempotency | consistency | owner |
| /v1/customers | GET | n/a | read-after-write | customer |
| /v1/customers | POST | required | strong | customer |
| /v1/customers/{id} | PATCH | required | strong | customer |
| /v1/customers/{id}/status | PUT | required | strong | customer |
| /v1/orders | POST | required | strong | ordering |
| /v1/orders/{id} | GET | n/a | read-after-write | ordering |
| /v1/orders/{id}/cancel | POST | required | strong | ordering |
| /v1/orders/{id}/lines | GET | n/a | read-after-write | ordering |
| /v1/payments/authorize | POST | required | strong | payments |
| /v1/payments/capture | POST | required | strong | payments |
| /v1/payments/refund | POST | required | eventual | payments |
| /v1/inventory/{sku} | GET | n/a | eventual | inventory |
| /v1/inventory/reserve | POST | required | strong | inventory |
| /v1/inventory/release | POST | required | strong | inventory |
| /v1/shipments | POST | required | eventual | fulfillment |
| /v1/shipments/{id} | GET | n/a | eventual | fulfillment |
| /v1/documents | POST | required | eventual | documents |
| /v1/documents/{id} | GET | n/a | eventual | documents |
| /v1/documents/{id}/text | GET | n/a | eventual | documents |
| /v1/documents/{id}/review | POST | required | strong | documents |
| /v1/search | GET | n/a | eventual | search |
| /v1/search/reindex | POST | required | eventual | search |
| /v1/reports/sales | POST | required | eventual | reporting |
| /v1/reports/{id} | GET | n/a | eventual | reporting |
| /v1/audit/events | GET | n/a | eventual | compliance |
| /v1/tenants | GET | n/a | strong | platform |
| /v1/tenants/{id}/limits | PATCH | required | strong | platform |
| /v1/feature-flags | GET | n/a | eventual | platform |
| /v1/health/live | GET | n/a | local | platform |
| /v1/health/ready | GET | n/a | local | platform |

## Response conventions

Every successful response includes a request correlation identifier. Collection
responses use `items`, `nextCursor` and `hasMore`; they never expose database
offsets. Error responses include `code`, `message`, `traceId` and optional
`details`. Clients must preserve unknown detail fields for diagnostics.

The following status mappings are historical and intentionally unrelated to the
target code. A conflict is 409, an invalid command is 422, an absent resource
is 404, an unauthenticated call is 401 and an unauthorized call is 403. Rate
limiting is 429 with a `Retry-After` header. Downstream timeout is 504 only at
the gateway boundary; internal services use a typed timeout error.

## Version compatibility notes

Version one clients may omit locale and receive `en-GB`. Version two clients
must send an explicit locale on report requests. The event envelope uses a
numeric revision, while the HTTP media type uses a dotted semantic version.
Never infer one version from the other. Unknown request fields are rejected on
commands but ignored on query parameters for backwards compatibility.

Pagination cursors are signed with a rotating key. A cursor remains valid for
twenty minutes and is bound to tenant, endpoint, sort order and filter hash.
Changing a filter while reusing a cursor returns `CURSOR_SCOPE_MISMATCH`.
Exports are asynchronous and expose a status resource until the download is
ready. A completed export is immutable and is deleted by retention policy.

## Security notes

Administrative endpoints require a step-up authentication claim. Service to
service calls use mTLS and a short-lived audience-bound token. User tokens are
never forwarded to downstream services. Audit entries redact email addresses
and all payment instrument data. Logs use a hash when correlating a sensitive
identifier across services.

## Operational notes

Each service exposes a build commit, schema revision and startup timestamp in
its diagnostic endpoint. Diagnostic endpoints are disabled on public ingress.
Circuit breaker state is exported as a metric but not returned to callers.
Queue depth alerts use a five-minute moving average. A deployment is healthy
only after two consecutive windows below the configured threshold.

The remainder of this catalog records stable names used by old clients:

alpha-customer-read, alpha-customer-write, alpha-order-read, alpha-order-write,
alpha-payment-authorize, alpha-payment-capture, alpha-payment-refund,
alpha-inventory-reserve, alpha-inventory-release, alpha-shipment-create,
alpha-document-upload, alpha-document-extract, alpha-document-review,
alpha-report-create, alpha-report-download, alpha-audit-search,
beta-customer-read, beta-customer-write, beta-order-read, beta-order-write,
beta-payment-authorize, beta-payment-capture, beta-payment-refund,
beta-inventory-reserve, beta-inventory-release, beta-shipment-create,
beta-document-upload, beta-document-extract, beta-document-review,
beta-report-create, beta-report-download, beta-audit-search,
gamma-customer-read, gamma-customer-write, gamma-order-read, gamma-order-write,
gamma-payment-authorize, gamma-payment-capture, gamma-payment-refund,
gamma-inventory-reserve, gamma-inventory-release, gamma-shipment-create,
gamma-document-upload, gamma-document-extract, gamma-document-review,
gamma-report-create, gamma-report-download, gamma-audit-search,
delta-customer-read, delta-customer-write, delta-order-read, delta-order-write,
delta-payment-authorize, delta-payment-capture, delta-payment-refund,
delta-inventory-reserve, delta-inventory-release, delta-shipment-create,
delta-document-upload, delta-document-extract, delta-document-review,
delta-report-create, delta-report-download, delta-audit-search,
epsilon-customer-read, epsilon-customer-write, epsilon-order-read, epsilon-order-write,
epsilon-payment-authorize, epsilon-payment-capture, epsilon-payment-refund,
epsilon-inventory-reserve, epsilon-inventory-release, epsilon-shipment-create,
epsilon-document-upload, epsilon-document-extract, epsilon-document-review,
epsilon-report-create, epsilon-report-download, epsilon-audit-search.
