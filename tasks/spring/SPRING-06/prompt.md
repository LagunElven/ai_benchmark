# Dynamic update with optimistic versioning

Implement `VersionedProfile.update`. A write succeeds only when `expectedVersion` is
the current version; then increment the version and update only non-null fields. A stale
write returns `false` and changes nothing. The operation must be atomic for concurrent
callers and must not use a global lock. Preserve existing fields when a patch omits them.
