# Saga associations

Implement `OrderSaga` association management. `start(orderId, associationKey)` creates
an active saga and associates the key with that order. `associate` adds another key to
the same active order. `orderFor(key)` resolves the order or returns `null`. `end(orderId)`
completes the saga and removes every association belonging to it; ending an unknown
order is a no-op. Ignore null/blank ids and keys, and do not let one order's keys resolve
to another order. Preserve the API and do not modify tests.
