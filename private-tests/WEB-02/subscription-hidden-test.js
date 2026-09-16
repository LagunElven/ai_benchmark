const { watch } = require('./subscription');

async function main() {
  let teardownCount = 0;
  let observer;
  let values = [];
  const subscription = watch({
    subscribe(valueObserver) {
      observer = valueObserver;
      valueObserver.next('sync');
      return { unsubscribe() { teardownCount += 1; } };
    },
  }, (value) => { values.push(value); });
  if (values.join(',') !== 'sync' || subscription.closed) {
    throw new Error('synchronous emission handling is incorrect');
  }
  subscription.unsubscribe();
  subscription.unsubscribe();
  observer.next('late');
  if (values.join(',') !== 'sync' || teardownCount !== 1 || !subscription.closed) {
    throw new Error('unsubscribe is not idempotent or values leaked');
  }

  let error;
  let errorTeardown = 0;
  const errored = watch({
    subscribe(valueObserver) {
      setTimeout(() => valueObserver.error(new Error('broken')), 0);
      return { unsubscribe() { errorTeardown += 1; } };
    },
  }, () => {}, (cause) => { error = cause; });
  await new Promise((resolve) => setTimeout(resolve, 10));
  if (!errored.closed || error?.message !== 'broken' || errorTeardown !== 1) {
    throw new Error('error did not close the subscription');
  }

  let completeTeardown = 0;
  const completed = watch({
    subscribe(valueObserver) {
      valueObserver.complete();
      return { unsubscribe() { completeTeardown += 1; } };
    },
  }, () => {});
  if (!completed.closed || completeTeardown !== 1) {
    throw new Error('synchronous completion was not cleaned up');
  }
  console.log('hidden subscription checks passed');
}

main().catch((cause) => { console.error(cause); process.exitCode = 1; });
