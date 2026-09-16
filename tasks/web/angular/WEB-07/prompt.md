# Cart state with signal and observable semantics

Implement `createCartStore(initialItems)`. The returned store exposes `getState()`,
`dispatch(action)` and `subscribe(listener)`. A state snapshot has `items`, `itemCount`
and `totalCents`; each item has `sku`, `quantity` and `unitCents`.

Support these actions: `{type: 'add', sku, quantity, unitCents}` adds a positive integer
quantity and merges an existing SKU, `{type: 'setQuantity', sku, quantity}` updates an
existing item and removes it for quantity zero, `{type: 'remove', sku}` removes an item,
and `{type: 'clear'}` empties the cart. Invalid actions and operations that change
nothing are ignored. Adding an existing SKU uses the new unit price.

Never mutate the initial items, actions or snapshots returned to callers. Notify each
subscriber synchronously exactly once after an effective change, passing a fresh
snapshot. `subscribe` returns an idempotent handle with `unsubscribe()` and a read-only
`closed` property; subscribing does not invoke the listener immediately.
