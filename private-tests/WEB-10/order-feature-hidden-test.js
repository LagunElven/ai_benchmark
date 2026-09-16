const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { createOrderService } = require('./order-service');
const { OrdersComponent } = require('./orders-component');

async function main() {
  let calls = 0;
  const service = createOrderService({
    async fetchOrder(id) {
      calls += 1;
      return { id, totalCents: 1, currency: ' CHF ' };
    },
  });
  assert.deepEqual(await service.loadOrder('o-1'), { id: 'o-1', amount: '0.01 CHF' });
  assert.equal(calls, 1);
  const jpy = createOrderService({
    async fetchOrder() { return { id: 'o-2', totalCents: 999, currency: 'JPY' }; },
  });
  assert.equal((await jpy.loadOrder('o-2')).amount, '9.99 JPY');

  let resolveRequest;
  const pendingService = { loadOrder: () => new Promise((resolve) => { resolveRequest = resolve; }) };
  const component = new OrdersComponent(pendingService);
  component.order = { id: 'stale', amount: '1.00 EUR' };
  const pending = component.load('new');
  if (!component.loading || component.order !== null || component.error !== null) {
    throw new Error('loading did not clear stale component state');
  }
  resolveRequest({ id: 'new', amount: '2.00 EUR' });
  assert.deepEqual(await pending, { id: 'new', amount: '2.00 EUR' });
  assert.equal(component.loading, false);

  const failed = new OrdersComponent({ loadOrder: async () => { throw new Error('backend detail'); } });
  failed.order = { id: 'stale', amount: '1.00 EUR' };
  assert.equal(await failed.load('missing'), null);
  assert.equal(failed.order, null);
  assert.equal(failed.error, 'Unable to load order');
  assert.equal(failed.loading, false);

  for (const dto of [
    {},
    { id: '', totalCents: 1, currency: 'EUR' },
    { id: 'o', totalCents: -1, currency: 'EUR' },
    { id: 'o', totalCents: 1.5, currency: 'EUR' },
    { id: 'o', totalCents: 1, currency: ' ' },
  ]) {
    const invalid = createOrderService({ async fetchOrder() { return dto; } });
    await invalid.loadOrder('o').then(
      () => { throw new Error('invalid DTO was accepted'); },
      () => undefined,
    );
  }
  const template = fs.readFileSync(path.join(__dirname, 'order-card.html'), 'utf8');
  if (!template.includes('order.id') || !template.includes('order.amount')
      || !template.includes('role="alert"') || template.includes('order.totalCents')) {
    throw new Error('template does not consume the service model');
  }
  console.log('hidden order feature checks passed');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
