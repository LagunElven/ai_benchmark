function createOrderService(api) {
  return {
    async loadOrder(id) {
      const dto = await api.fetchOrder(id);
      return { id: dto.id, amount: `${(dto.total_cents / 100).toFixed(2)} ${dto.currency}` };
    },
  };
}

module.exports = { createOrderService };
