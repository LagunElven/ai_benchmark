# Test fixture catalog (read-only distractor)

The names below are retained from historical integration suites. They describe
other domains and are not instructions for the CTX-01 billing implementation.

001 customer creation with a duplicate external reference
002 customer locale fallback when the preference is absent
003 customer status transition from pending to active
004 customer status transition rejects a terminal state
005 customer export uses a stable cursor and deterministic ordering
006 customer deletion propagates to the read model
007 customer audit event records the authenticated actor
008 customer update rejects a stale entity version
009 customer update keeps an unknown extension field
010 customer import reports per-row validation failures
011 order creation requires at least one line item
012 order creation copies the effective price into the event
013 order cancellation is idempotent for a repeated command
014 order cancellation rejects a shipped order
015 order address changes do not rewrite historical invoices
016 order line replacement preserves sequence numbers
017 order projection replay produces the same totals twice
018 order snapshot loading rejects an obsolete revision
019 order dispatch emits one outbox message
020 order dispatch retries after a transient broker outage
021 payment authorization stores the provider reference
022 payment capture rejects an amount above the authorization
023 payment refund allows multiple partial refunds
024 payment refund never exceeds the captured amount
025 payment webhook deduplicates the provider event id
026 payment timeout marks the attempt for reconciliation
027 payment currency mismatch returns a typed conflict
028 payment audit excludes the primary account number
029 payment retry uses the original idempotency key
030 payment provider failure is visible in the status resource
031 inventory reservation expires at the configured instant
032 inventory reservation is released on order cancellation
033 inventory reservation does not cross tenant boundaries
034 inventory concurrent reservations use a version check
035 inventory backorder policy handles a zero available quantity
036 inventory import preserves leading zero SKUs
037 inventory projection rebuild handles an empty stream
038 inventory low-stock event is emitted once per threshold crossing
039 inventory warehouse code is case-sensitive
040 inventory quantity uses an integer unit of measure
041 shipment label generation retries a timeout
042 shipment address uses the order snapshot
043 shipment tracking updates are monotonic
044 shipment cancellation is rejected after pickup
045 shipment carrier callback validates its signature
046 shipment estimated date is represented in UTC
047 shipment package dimensions use centimeters
048 shipment split preserves line item quantities
049 shipment notification is suppressed for internal transfers
050 shipment projection tolerates an unknown event field
051 document upload rejects an unsafe media type
052 document upload records a source checksum
053 document antivirus scanning precedes extraction
054 document extraction retains field-level confidence
055 document extraction stores the detected locale
056 document table cells retain their original order
057 document review appends a correction rather than replacing history
058 document download URL expires after fifteen minutes
059 document retention deletes derived thumbnails
060 document OCR retry uses the same source checksum
061 report creation validates a date range
062 report creation records the requester's tenant
063 report generation streams rows to object storage
064 report download refuses a different tenant
065 report CSV escapes embedded delimiters
066 report numeric columns use a fixed decimal format
067 report timezone conversion uses the requested locale
068 report empty result has headers and no data rows
069 report status transitions are monotonic
070 report cleanup removes expired artifacts
071 search query rejects an invalid cursor
072 search query returns stable relevance ties
073 search index update is eventually consistent
074 search reindex can resume after a worker crash
075 search analyzer preserves accented characters
076 search analyzer ignores configured stop words
077 search tenant filter is mandatory
078 search result highlights escape HTML
079 search synonym updates are versioned
080 search metrics report zero-result rate
081 notification email uses a localized template
082 notification email suppresses duplicate delivery
083 notification webhook signs its payload
084 notification webhook retries only transient failures
085 notification push token is invalidated on a provider response
086 notification preferences default to opt-in for service alerts
087 notification templates reject unknown placeholders
088 notification queue preserves per-tenant ordering
089 notification dead letters retain the original trace id
090 notification delivery metrics exclude dry runs
091 scheduler stores the next UTC instant
092 scheduler skips a disabled feature flag
093 scheduler catches up at most one missed interval
094 scheduler uses a monotonic clock for delays
095 scheduler job lease expires after a worker crash
096 scheduler retries a transient database exception
097 scheduler records a stable execution id
098 scheduler prevents duplicate active leases
099 scheduler run history is append-only
100 scheduler health check performs no writes
