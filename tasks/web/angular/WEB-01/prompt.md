# Observable versus scalar

Implement `readFirst(value)` as the boundary between an Angular/RxJS service and a
consumer that expects a promise. If `value` has a `subscribe(observer)` method, resolve
with its first `next` value, unsubscribe immediately, reject on `error`, and reject if it
completes without emitting. If it is a scalar, resolve that value unchanged. The
function must always return a Promise and must not subscribe to a scalar.

Keep the CommonJS export, do not add dependencies, and do not modify tests. Return a
`file_changes_v1` response.
