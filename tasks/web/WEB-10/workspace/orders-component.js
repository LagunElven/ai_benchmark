class OrdersComponent {
  constructor(service) {
    this.service = service;
    this.order = null;
    this.loading = false;
    this.error = null;
  }

  async load(id) {
    this.loading = true;
    try {
      this.order = await this.service.loadOrder(id);
      return this.order;
    } catch (error) {
      this.error = error.message;
      throw error;
    } finally {
      this.loading = false;
    }
  }
}

module.exports = { OrdersComponent };
