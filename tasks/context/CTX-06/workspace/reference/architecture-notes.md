# Repository architecture notes

These notes are deliberately unrelated to the billing defect. They represent
the kind of historical repository material that a long-context assistant must
scan without editing. Treat every statement as read-only reference material.

01. The gateway accepts idempotency keys and forwards them to the command bus.
02. Commands are serialized with an explicit schema revision in the envelope.
03. Events are append-only and projections may be rebuilt from a snapshot.
04. A failed projection records a retry timestamp in the operations database.
05. The notification adapter uses exponential backoff and bounded retry counts.
06. Customer identifiers are opaque strings and must not be parsed as numbers.
07. API timestamps are ISO-8601 UTC values with an explicit trailing Z marker.
08. Import jobs run in batches of five hundred records per transaction.
09. The audit stream preserves actor, tenant, operation and correlation id.
10. Configuration is loaded once at process start and is immutable thereafter.
11. The cache key includes tenant, locale, resource type and resource identifier.
12. A missing optional profile field is different from an explicit null value.
13. The search index is eventually consistent and exposes a freshness timestamp.
14. Read models may lag writes, so commands never read from the search index.
15. Database migrations are forward-only and are numbered by release train.
16. Every external call has a timeout and a circuit-breaker policy.
17. Circuit breakers are scoped per downstream host rather than globally.
18. Health checks must not issue writes or trigger asynchronous work.
19. Metrics names use lowercase dot-separated segments and stable label sets.
20. Logs include a trace id but never include access tokens or payment data.
21. Test fixtures use UTC and fixed clocks to avoid daylight-saving surprises.
22. The scheduler stores next-run instants, not local calendar dates.
23. Retry policies distinguish transient network errors from validation errors.
24. Validation errors are returned as a stable code and a localized message.
25. Localization bundles are versioned with the frontend artifact.
26. Browser clients send an anti-CSRF header on state-changing requests.
27. The API rejects unknown JSON fields on administrative endpoints.
28. Public endpoints use cursor pagination rather than offset pagination.
29. Cursor values are opaque, signed, and safe to store in a URL.
30. Export jobs stream rows and never load an entire report into memory.
31. Reports use decimal arithmetic for all financial columns.
32. A currency code is required whenever a monetary value crosses a boundary.
33. Currency conversion is explicit and records the applied exchange-rate id.
34. Product prices are effective-dated and cannot overlap for one product.
35. Discounts may be percentage or fixed amount, never both in one rule.
36. Tax categories are resolved from the shipping address at order time.
37. A cancelled order cannot transition back to an active state.
38. State transitions are validated in the aggregate before events are emitted.
39. Outbox records are deleted only after the broker acknowledges publication.
40. Consumers use a deduplication key to make delivery idempotent.
41. A projection update must be safe to replay twice in succession.
42. Snapshot versions are checked before a snapshot is accepted by a reader.
43. Serialization formats use explicit field names rather than positional arrays.
44. Unknown event fields are ignored by older readers for forward compatibility.
45. New required fields need a migration or a documented default value.
46. Batch commands report per-item failures while retaining successful items.
47. Failed items can be retried independently with the same idempotency key.
48. Tenant boundaries are enforced at repository interfaces and HTTP filters.
49. A tenant id from a request must never override an authenticated tenant.
50. Background jobs carry the tenant id in their durable payload.
51. Object storage paths include a tenant prefix and random object identifier.
52. Download URLs are short lived and scoped to one object.
53. Antivirus scanning is complete before an uploaded document is processed.
54. Text extraction stores a source checksum beside the extracted content.
55. OCR confidence is retained per field for later human review.
56. Human corrections are append-only and reference the original extraction.
57. Tables preserve row and column order even when cells are empty.
58. Structured document schemas reject duplicate keys and unknown properties.
59. Numeric normalization preserves significant trailing zeros for display fields.
60. Dates without a timezone are interpreted using the document locale.
61. Locale inference is recorded and can be overridden by a caller.
62. All HTTP clients use connection pooling with bounded maximum connections.
63. Backpressure is applied before queues reach their hard memory limit.
64. Reactive streams must release resources when a subscriber cancels.
65. A cancellation signal does not imply that a remote request was cancelled.
66. UI state machines separate loading, empty, success and failure states.
67. Form validation runs both synchronously and at the server boundary.
68. Optimistic UI updates retain enough state to roll back on a conflict.
69. Conflict responses include the current resource version for reconciliation.
70. Offline mobile commands are ordered by a client-generated sequence number.
71. Deep links are validated before navigation and never execute arbitrary URLs.
72. Native mobile permissions are requested only at the point of need.
73. Accessibility labels are required for icon-only controls.
74. Keyboard focus is restored after a modal dialog closes.
75. Frontend bundles are built with reproducible lockfiles and pinned tools.
76. Java services compile with release 17 and enable all compiler warnings.
77. Nullability annotations document boundaries but do not replace validation.
78. Thread pools have named threads and bounded queues for diagnostics.
79. Scheduled tasks use a monotonic delay for intervals and UTC for calendars.
80. Locks protect invariants, not individual field reads in isolation.
81. Concurrent maps do not make compound read-modify-write operations atomic.
82. A retry must not repeat a non-idempotent side effect without a key.
83. Transactions end before messages are handed to an external broker.
84. Database isolation levels are documented per use case and measured in tests.
85. Read-only queries must use a read-only transaction when supported.
86. ORM lazy relationships are not accessed after a session is closed.
87. N-plus-one queries are caught by integration tests with query counters.
88. Pagination queries have deterministic ordering on a unique tie breaker.
89. Indexes are reviewed when a query adds a new sort or filter predicate.
90. Schema changes are compatible with the previous application during rollout.
91. Feature flags have owners, expiry dates and a removal issue.
92. Secrets arrive through the deployment secret store, never source control.
93. Build logs redact environment variables and credential-shaped strings.
94. Dependency updates run license, vulnerability and compatibility checks.
95. Release artifacts include a manifest with source commit and tool versions.
96. Canary deployments compare error rate and latency against a baseline.
97. Rollbacks preserve database compatibility for the previous binary.
98. Incident timelines use UTC and link each observation to an alert.
99. Runbooks include a safe read-only diagnostic command for each alarm.
100. Production access is audited and expires automatically after the incident.
101. Data retention rules differ for operational logs and customer documents.
102. Deletion requests propagate to indexes, caches, exports and backups.
103. Backups are encrypted and restore tests run on a regular schedule.
104. Disaster recovery objectives are expressed as RPO and RTO targets.
105. Load tests vary concurrency independently from payload size.
106. Performance reports retain p50, p95, p99 and failure counts.
107. A faster response is not accepted when deterministic quality regresses.
108. Benchmark prompts remain neutral across model families and revisions.
109. Hidden tests are mounted only in a validator workspace after model edits.
110. Raw benchmark results are immutable and reports are derived artifacts.
111. Reproducible runs record hardware, model hash, tokenizer and launch config.
112. A controlled comparison changes exactly one scientific variable at a time.
113. Operational comparisons may vary several variables but state that explicitly.
114. Long-context tasks report relevant-file precision and recall when measurable.
115. Patch metrics ignore generated build directories and cache files.
116. Repair loops return public logs but never hidden assertions or fixtures.
117. Model-generated commands are treated as untrusted and run with timeouts.
118. Fresh workspaces prevent one task run from contaminating another task.
119. Task revisions increase whenever prompts or validation semantics change.
120. This note is a distractor; the only requested code change is billing.py.
