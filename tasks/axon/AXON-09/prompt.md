# Optimistic locking and retry

Implement `OptimisticCommandHandler.apply`. A command succeeds only when its expected
aggregate version equals the current version, then increments the version and balance
by `delta`. A stale version must throw `ConflictException` without changing state.
`applyWithRetry` may retry a conflict using the current version, but must stop after
`maxAttempts` and propagate the final conflict; do not catch unrelated runtime errors.
Reject non-positive attempt limits and preserve the nested API.
