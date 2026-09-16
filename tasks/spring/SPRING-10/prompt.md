# Consistent multi-service checkout

Implement `CheckoutCoordinator.complete`. The order service and payment service do not
share a transaction. A pending order must be charged before it is marked `PAID`, and an
order that is already paid must not be charged again. A payment exception is atomic (no
charge was made): mark the order `PAYMENT_FAILED` and propagate the original exception.

If charging succeeds but the order update fails, attempt a payment refund, preserve the
original update exception (including a refund failure as suppressed information), and do
not report success. A failed order may be retried. Do not swallow failures, add global
locking, or modify the public tests; keep the existing Java API.
