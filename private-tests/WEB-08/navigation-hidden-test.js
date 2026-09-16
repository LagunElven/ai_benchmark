const { createNavigator } = require('./navigation');

async function main() {
  const calls = [];
  const navigator = createNavigator('/home', async (from, to) => {
    calls.push(`${from}->${to}`);
    return to !== '/blocked';
  });
  await navigator.navigate('/orders');
  const blocked = await navigator.navigate('/blocked');
  if (blocked !== '/orders' || navigator.current() !== '/orders'
      || calls.join(',') !== '/home->/orders,/orders->/blocked') {
    throw new Error('false async guard committed a route');
  }
  await navigator.replace('/order/1');
  if (JSON.stringify(navigator.history()) !== JSON.stringify(['/home', '/order/1'])) {
    throw new Error('replace changed the stack incorrectly');
  }
  const exposed = navigator.history();
  exposed.push('/tampered');
  if (navigator.current() !== '/order/1' || navigator.history().length !== 2) {
    throw new Error('history was exposed mutably');
  }

  let guardCalls = 0;
  const root = createNavigator('/root', (from, to) => {
    guardCalls += 1;
    return to !== '/root';
  });
  if (await root.back() !== '/root' || guardCalls !== 0) {
    throw new Error('root back invoked the guard');
  }
  await root.navigate('/edit');
  if (guardCalls !== 1 || root.current() !== '/edit') {
    throw new Error('guarded navigate was not committed');
  }
  if (await root.back() !== '/edit' || guardCalls !== 2 || root.current() !== '/edit') {
    throw new Error('guarded back was not cancelled');
  }

  const rejecting = createNavigator('/a', () => { throw new Error('guard failed'); });
  try {
    await rejecting.navigate('/b');
    throw new Error('guard rejection was swallowed');
  } catch (error) {
    if (error.message !== 'guard failed') throw error;
  }
  if (JSON.stringify(rejecting.history()) !== JSON.stringify(['/a'])) {
    throw new Error('rejected transition changed history');
  }
  console.log('hidden navigation checks passed');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
