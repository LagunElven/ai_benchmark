# Concurrent audit sequence

Fix `AuditSequence.nextId`. Each call must return a unique, monotonically increasing
identifier, starting at the constructor's `initial` value. Calls from multiple threads
must not duplicate or skip identifiers. Reject an initial value below zero. Keep the
public API, do not use a process-global lock, and do not modify tests.
