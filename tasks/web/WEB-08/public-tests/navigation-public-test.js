const { createNavigator } = require('../navigation');

async function main() {
  const navigator = createNavigator('/home', () => true);
  await navigator.navigate('/orders');
  if (navigator.current() !== '/orders'
      || JSON.stringify(navigator.history()) !== JSON.stringify(['/home', '/orders'])) {
    throw new Error('navigation push failed');
  }
  await navigator.back();
  if (navigator.current() !== '/home') throw new Error('navigation back failed');
  console.log('public navigation checks passed');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
