function watch(source, onValue, onError) {
  if (!source || typeof source.subscribe !== 'function' || typeof onValue !== 'function') {
    throw new TypeError('source and onValue are required');
  }
  let closed = false;
  let teardown;
  let teardownReady = false;

  const runTeardown = () => {
    if (!teardownReady) return;
    const current = teardown;
    teardown = undefined;
    teardownReady = false;
    if (typeof current === 'function') current();
    else if (current && typeof current.unsubscribe === 'function') current.unsubscribe();
  };
  const close = () => {
    if (closed) return;
    closed = true;
    runTeardown();
  };
  const observer = {
    next(value) {
      if (!closed) onValue(value);
    },
    error(error) {
      if (closed) return;
      closed = true;
      runTeardown();
      if (typeof onError === 'function') onError(error);
    },
    complete() {
      if (closed) return;
      closed = true;
      runTeardown();
    },
  };

  teardown = source.subscribe(observer);
  teardownReady = true;
  if (closed) runTeardown();
  return { unsubscribe: close, get closed() { return closed; } };
}

module.exports = { watch };
