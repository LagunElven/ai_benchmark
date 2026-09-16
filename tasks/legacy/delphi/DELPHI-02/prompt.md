# DELPHI-02 — Delphi owned-resource lifecycle

Read `legacy/ResourceOwner.pas` and complete the Java target
`ResourceOwner`.

The Delphi owner creates one owned resource for every supplied name. Its
destructor calls `Close`, and `Close` releases every owned resource, marks the
owner closed, and is safe to call repeatedly. Preserve input order and make a
defensive copy of the supplied list. `close()` must release each resource at
most once, `activeNames()` must expose a read-only snapshot, and the class must
implement `AutoCloseable`.

Reject a null list with `IllegalArgumentException`; otherwise preserve the
names, including an empty list. Keep the public API and do not modify the
legacy source or tests. Return only the `file_changes_v1` JSON object.
