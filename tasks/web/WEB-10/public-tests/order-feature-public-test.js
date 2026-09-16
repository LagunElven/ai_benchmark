const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const api = require('../api');
const { createOrderService } = require('../order-service');
const { OrdersComponent } = require('../orders-component');

async function main() {
  const component = new OrdersComponent(createOrderService(api));
  const loaded = await component.load('o-1');
  assert.deepEqual(loaded, { id: 'o-1', amount: '12.50 EUR' });
  assert.deepEqual(component.order, loaded);
  assert.equal(component.loading, false);
  assert.equal(component.error, null);
  const template = fs.readFileSync(path.join(__dirname, '..', 'order-card.html'), 'utf8');
  assert.match(template, /order\.id/);
  assert.match(template, /order\.amount/);
  console.log('public order feature checks passed');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
