# SPRING-05 — optimistic locking

`OptimisticStock` is a small framework-free harness representing a JPA entity
with a `@Version` column. Fix `update` so a write based on an old `Snapshot`
cannot silently overwrite a newer write. A stale update must throw the nested
`OptimisticStock.ConflictException`; a current update must replace the quantity
and increment the version exactly once. Preserve the public API, ordering and
thread safety. Do not modify tests. Return only the `file_changes_v1` JSON object.

The harness deliberately has no Spring or database dependency; the behavior is
the deterministic contract that a Spring/JPA implementation must provide.
