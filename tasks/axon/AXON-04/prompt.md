# Snapshot filtering

Implement `SnapshotPolicy.shouldLoad`. Reject an obsolete snapshot only when its
aggregate type matches the requested aggregate type and its revision is below the
minimum supported revision. Snapshots for another aggregate type must remain eligible,
as must the exact minimum revision. Null types or negative revisions are invalid and
must return `false`; do not modify tests.
