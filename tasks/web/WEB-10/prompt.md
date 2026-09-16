# Cross-layer order feature

Complete the Web feature spanning `api.js`, `order-service.js`, `orders-component.js` and
`order-card.html`. The API is fixed and returns the wire DTO
`{id, totalCents, currency}`; do not modify it. The service factory
`createOrderService(api)` must expose `loadOrder(id)`, validate that DTO, and return the
UI model `{id, amount}` where amount is formatted as exact cents with two decimal places
followed by a trimmed currency (for example `12.50 EUR`). Reject malformed, negative or
non-integer totals.

`OrdersComponent.load(id)` must set `loading` while awaiting the service, clear stale
order and error state before starting, store the model on success, and on failure clear
the order, set the stable message `Unable to load order`, return `null` and finish with
`loading === false`. Return the loaded model on success. The template must display the
order id and amount only when a non-loading order exists, and display the error as an
alert when loading has failed. Preserve the API and tests; do not add dependencies.
