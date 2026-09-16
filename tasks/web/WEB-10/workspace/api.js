async function fetchOrder(orderId) {
  return { id: orderId, totalCents: 1250, currency: 'EUR' };
}

module.exports = { fetchOrder };
