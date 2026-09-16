# Subscription lifecycle

Implement `watch`. It subscribes to an RxJS-style source with `next`, `error` and
`complete` callbacks and returns a handle exposing `unsubscribe()` and a read-only
`closed` property. Values must reach `onValue` only while the subscription is active.

Calling `unsubscribe()` must be idempotent, stop later values, and invoke the source
teardown exactly once. Completion and errors must also close and tear down the
subscription; errors are delivered to the optional `onError` callback. Sources may emit
synchronously before `subscribe` returns. Do not use a real RxJS dependency or modify
the tests.
