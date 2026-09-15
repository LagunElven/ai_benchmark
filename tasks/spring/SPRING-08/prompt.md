# Non-blocking asynchronous retry

Implement `AsyncRetry.retry`. Invoke the asynchronous operation immediately and retry
after an exceptional completion until it succeeds or `maxAttempts` is reached. Return
one `CompletionStage` carrying the first success or the final failure. Retries must be
scheduled through the supplied `ScheduledExecutorService` (never `Thread.sleep` or a
blocking wait), and `maxAttempts` must be positive. Preserve the generic API and do not
modify tests.
