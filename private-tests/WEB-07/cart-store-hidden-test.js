const { createCartStore } = require('./cart-store');

const initial = [{ sku: 'A-1', quantity: 2, unitCents: 500 }];
const store = createCartStore(initial);
const firstSnapshot = store.getState();
firstSnapshot.items[0].quantity = 99;
if (store.getState().itemCount !== 2 || store.getState().totalCents !== 1000
    || initial[0].quantity !== 2) {
  throw new Error('state or input was exposed mutably');
}

let notifications = 0;
let latest;
const subscription = store.subscribe((state) => { notifications += 1; latest = state; });
store.dispatch({ type: 'add', sku: 'A-1', quantity: 3, unitCents: 600 });
if (notifications !== 1 || latest.totalCents !== 3000 || latest.items[0].unitCents !== 600) {
  throw new Error('existing SKU was not merged with the new price');
}
store.dispatch({ type: 'setQuantity', sku: 'A-1', quantity: 0 });
if (notifications !== 2 || store.getState().items.length !== 0) {
  throw new Error('zero quantity did not remove the item');
}
store.dispatch({ type: 'setQuantity', sku: 'missing', quantity: 2 });
store.dispatch({ type: 'remove', sku: 'missing' });
store.dispatch({ type: 'add', sku: '', quantity: 1, unitCents: 10 });
store.dispatch({ type: 'add', sku: 'B-1', quantity: 0, unitCents: 10 });
if (notifications !== 2) throw new Error('invalid or no-op actions notified subscribers');

subscription.unsubscribe();
subscription.unsubscribe();
store.dispatch({ type: 'add', sku: 'B-1', quantity: 1, unitCents: 125 });
if (notifications !== 2 || !subscription.closed) {
  throw new Error('subscription cleanup is not idempotent');
}
const after = store.getState();
after.items[0].quantity = 50;
if (store.getState().items[0].quantity !== 1) throw new Error('later snapshot was shared');
store.dispatch({ type: 'clear' });
if (store.getState().itemCount !== 0 || store.getState().totalCents !== 0) {
  throw new Error('clear did not reset derived state');
}
console.log('hidden cart-store checks passed');
