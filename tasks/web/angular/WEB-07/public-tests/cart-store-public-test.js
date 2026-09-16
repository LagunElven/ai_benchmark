const { createCartStore } = require('../cart-store');

const initial = [{ sku: 'A-1', quantity: 2, unitCents: 500 }];
const store = createCartStore(initial);
let observed;
const subscription = store.subscribe((state) => { observed = state; });
store.dispatch({ type: 'add', sku: 'A-1', quantity: 1, unitCents: 500 });
const state = store.getState();
if (state.itemCount !== 3 || state.totalCents !== 1500 || state.items.length !== 1) {
  throw new Error('cart derived state or merge behavior is wrong');
}
if (!observed || observed.itemCount !== 3 || initial[0].quantity !== 2) {
  throw new Error('cart update was not published immutably');
}
subscription.unsubscribe();
console.log('public cart-store checks passed');
