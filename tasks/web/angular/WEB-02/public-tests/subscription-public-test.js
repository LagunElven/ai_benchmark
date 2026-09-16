const { watch } = require('../subscription');

let delivered = 0;
let stopped = 0;
let observer;
const source = {
  subscribe(nextObserver) {
    observer = nextObserver;
    return { unsubscribe() { stopped += 1; } };
  },
};
const subscription = watch(source, () => { delivered += 1; });
observer.next('first');
subscription.unsubscribe();
observer.next('late');
if (delivered !== 1 || stopped !== 1 || !subscription.closed) {
  throw new Error('explicit subscription cleanup failed');
}
console.log('public subscription checks passed');
