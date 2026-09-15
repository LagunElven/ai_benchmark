# Multiple saga start paths

Two event paths can start an order saga: `onOrderPlaced` associates the order with a
customer key, while `onPaymentRequested` associates it with a payment key. Both paths
for the same order must resolve to one active saga, not two. `activeSagas` reports the
number of distinct active orders; `orderFor` resolves a key or returns `null`; `end`
removes every key for that order. Ignore null/blank values and preserve independent
orders. Keep the API and do not modify tests.
