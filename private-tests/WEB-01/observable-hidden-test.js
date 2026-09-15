const { readFirst } = require('./observable');

async function main() {
  let unsubscribed = 0;
  const observable = {
    subscribe(observer) {
      setTimeout(() => observer.next('first'), 0);
      setTimeout(() => observer.next('second'), 5);
      return { unsubscribe() { unsubscribed += 1; } };
    },
  };
  if (await readFirst(observable) !== 'first' || unsubscribed !== 1) {
    throw new Error('first emission was not resolved and unsubscribed');
  }
  await readFirst({
    subscribe(observer) { observer.error(new Error('boom')); return { unsubscribe() {} }; },
  }).then(() => { throw new Error('error was swallowed'); }, () => undefined);
  await readFirst({
    subscribe(observer) { observer.complete(); return { unsubscribe() {} }; },
  }).then(() => { throw new Error('empty observable was accepted'); }, () => undefined);
  console.log('hidden observable checks passed');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
