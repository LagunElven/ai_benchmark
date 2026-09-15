# Domain glossary and compatibility aliases

This glossary is supplied as historical repository context. It is intentionally
not a specification for the billing function and must not be edited.

| term | meaning | legacy alias | owner |
| account | billable organization boundary | client | customer |
| actor | authenticated principal making a change | user | security |
| aggregate | consistency boundary for commands | root entity | ordering |
| allocation | quantity assigned to a warehouse | allotment | inventory |
| amount | decimal monetary value with currency | value | finance |
| authorization | permission to perform an operation | grant | security |
| backorder | requested stock not currently available | pending stock | inventory |
| batch | group of records processed together | page | platform |
| beneficiary | party receiving a payment | payee | payments |
| booking | reserved capacity on a calendar | reservation | scheduling |
| boundary | interface between independently deployed code | seam | architecture |
| capture | finalization of an authorized payment | settle | payments |
| checksum | digest identifying source bytes | fingerprint | documents |
| claim | token attribute granted by an identity provider | assertion | security |
| cursor | opaque continuation marker for a collection | bookmark | api |
| customer | organization or person buying services | account | customer |
| dead letter | message that exhausted delivery attempts | poison item | messaging |
| discount | reduction applied before tax | rebate | finance |
| dispatch | handoff of an order to fulfillment | release | fulfillment |
| document | source file submitted for processing | artifact | documents |
| draft | mutable order before confirmation | quote | ordering |
| envelope | metadata surrounding an event payload | wrapper | messaging |
| event | immutable fact emitted by an aggregate | notification | messaging |
| exchange rate | factor used to convert currencies | fx rate | finance |
| extraction | structured fields derived from a document | parsing | documents |
| feature flag | runtime switch with an owner and expiry | toggle | platform |
| fulfillment | process delivering goods or services | shipping | fulfillment |
| gateway | ingress boundary for external requests | edge | api |
| idempotency | repeated command has one effect | deduplication | platform |
| invoice | financial record of supplied services | bill | finance |
| item | one product or service in a document | line | ordering |
| lease | time-bounded ownership of a worker job | lock | platform |
| locale | language and regional formatting preferences | culture | customer |
| ledger | append-only financial record | journal | finance |
| line | one order or invoice entry | item | ordering |
| manifest | list of files and versions in an artifact | inventory | release |
| merchant | organization receiving a payment | vendor | payments |
| message | transport unit delivered to a consumer | envelope | messaging |
| migration | forward-only change to persistent structure | upgrade | database |
| outbox | durable message waiting for publication | relay | messaging |
| payment | attempt to move money between parties | transaction | payments |
| projection | read model built from events | view | ordering |
| promise | asynchronous result in a browser client | future | web |
| projection | query-oriented representation of facts | read model | ordering |
| reconciliation | process comparing two external records | matching | finance |
| reference | human-readable identifier for a resource | number | api |
| replay | rebuilding a projection from its event stream | rebuild | ordering |
| reservation | temporary hold on inventory or capacity | allocation | inventory |
| revision | version of a serialized event or schema | sequence | messaging |
| rollback | restoring application behavior after release | revert | release |
| saga | coordinated long-running business process | workflow | ordering |
| settlement | completed transfer of funds | capture | payments |
| snapshot | saved aggregate state at a stream position | checkpoint | ordering |
| source | original bytes supplied for processing | input | documents |
| status | current lifecycle state of a resource | state | api |
| subtotal | sum before discount and tax | net amount | finance |
| tenant | isolated customer boundary in shared infrastructure | realm | platform |
| tax | government charge applied after discount | levy | finance |
| trace | linked observations across services | correlation | operations |
| upcaster | converter from an old event revision | migrator | messaging |
| webhook | signed callback sent to an external endpoint | callback | integrations |
| workspace | isolated files used by one benchmark run | sandbox | benchmark |

## Compatibility aliases

The old billing service called `subtotal` `net_amount`, `discount_percent`
`rebate_rate`, and `tax_percent` `vat_rate`. The public benchmark contract uses
the current names. The aliases are retained here to make repository search
non-trivial, not to authorize changing the function signature.

The old order service called a line `detail`, a quantity `units`, and a unit
price `rate`. Those names occur in archived fixtures and should not be copied
into current code. The payment service called a transaction `attempt` until
capture succeeded; after capture it became a settlement. The document service
uses `field confidence` while the OCR vendor uses `score`; they are related but
not interchangeable values.

## Identifier formats

Customer IDs begin with `cus_`, orders with `ord_`, invoices with `inv_`, and
documents with `doc_`. These prefixes are opaque and are never used for numeric
sorting. External provider references may contain letters, digits, slashes and
hyphens. Correlation IDs are UUIDs in new traffic and legacy hex strings in
archived logs. A parser must retain them as strings.

## Decimal and date conventions

Financial amounts use a decimal point and two display places. Storage may retain
more precision for exchange rates, but the invoice display is rounded once at
the final boundary. Date-only fields use the tenant locale; event timestamps
use UTC instants. A date without a timezone is not an instant until a locale is
known. These notes describe unrelated services and are not an excuse to change
the CTX-01 input types.

## Operational labels

`cold_start` means no process-local cache, `warm` means a cache entry exists,
`shared_prefix` means common request context, and `distinct_prefix` means each
request carries independent context. These labels belong to serving benchmarks,
not quality tasks. `pass_at_1` and `pass_at_3` belong to repair reporting and are
computed from raw validation outcomes rather than inferred from logs.
