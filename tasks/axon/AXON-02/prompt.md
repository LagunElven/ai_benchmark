# AXON-02 — revision upcaster

Implement the revision-zero to revision-one upcaster for an `OrderCreated`
event. Revision `0` stores the monetary field as `totalCents`; revision `1`
renames it to `amountCents` and adds `currency=EUR`. Return a new payload and
never mutate the caller's map. Revision `1` must pass through unchanged,
including unknown extra fields. Reject unsupported revisions with
`IllegalArgumentException`. Preserve the public records and return only the
`file_changes_v1` JSON object.

This is a dependency-free harness for the equivalent Axon upcaster contract;
the hidden tests cover immutability and the already-current revision.
