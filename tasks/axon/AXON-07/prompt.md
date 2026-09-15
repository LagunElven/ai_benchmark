# Idempotent order projection

`OrderProjection.apply` consumes replayable events. Apply an event's status to its
order exactly once per non-blank event id; a duplicate delivery must have no effect.
Events for different orders remain independent, and the latest distinct event for an
order wins. Ignore null events, blank ids and blank order ids. The projection must be
safe when two threads apply events concurrently and `status(orderId)` returns `null`
when no projection exists. Preserve the API and do not modify tests.
