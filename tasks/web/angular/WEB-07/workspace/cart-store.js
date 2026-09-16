function createCartStore(initialItems) {
  const items = initialItems || [];
  const listeners = [];
  return {
    getState() {
      return {
        items,
        itemCount: items.length,
        totalCents: items.reduce((total, item) => total + item.quantity * item.unitCents, 0),
      };
    },
    dispatch(action) {
      if (action?.type === 'add') {
        items.push({ sku: action.sku, quantity: action.quantity, unitCents: action.unitCents });
        listeners.forEach((listener) => listener(this.getState()));
      }
    },
    subscribe(listener) {
      listeners.push(listener);
      return () => listeners.splice(listeners.indexOf(listener), 1);
    },
  };
}

module.exports = { createCartStore };
