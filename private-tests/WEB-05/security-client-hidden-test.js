const { withSafeCredentials } = require('./security-client');

const origin = 'https://app.example.test';
const crossOrigin = {
  method: 'POST',
  url: 'https://evil.example.test/collect',
  headers: { authorization: 'old', 'X-CSRF-TOKEN': 'old-csrf', Accept: 'json' },
};
const safe = withSafeCredentials(crossOrigin, 'secret', 'csrf', origin);
if (Object.keys(safe.headers).some((name) =>
  name.toLowerCase() === 'authorization' || name.toLowerCase() === 'x-csrf-token')) {
  throw new Error('credentials leaked cross-origin');
}
if (crossOrigin.headers.authorization !== 'old' || crossOrigin.headers['X-CSRF-TOKEN'] !== 'old-csrf') {
  throw new Error('cross-origin request was mutated');
}

const duplicateHeaders = {
  method: 'PATCH',
  url: '/orders/1',
  headers: {
    authorization: 'old-a',
    Authorization: 'old-b',
    'x-csrf-token': 'old-a',
    'X-CSRF-Token': 'old-b',
    Accept: 'json',
  },
};
const updated = withSafeCredentials(duplicateHeaders, '  token  ', '  csrf  ', origin);
const securityEntries = Object.entries(updated.headers);
if (securityEntries.filter(([name]) => name.toLowerCase() === 'authorization').length !== 1
    || updated.headers.Authorization !== 'Bearer token') {
  throw new Error('authorization was not canonically replaced');
}
if (securityEntries.filter(([name]) => name.toLowerCase() === 'x-csrf-token').length !== 1
    || updated.headers['X-CSRF-Token'] !== 'csrf') {
  throw new Error('CSRF was not canonically replaced');
}

for (const method of ['GET', 'HEAD', 'OPTIONS']) {
  const noCsrf = withSafeCredentials(
    { method, url: '/orders', headers: { 'x-csrf-token': 'stale' } }, ' ', '', origin);
  if (Object.keys(noCsrf.headers).some((name) => name.toLowerCase() === 'x-csrf-token')) {
    throw new Error(`${method} received a CSRF header`);
  }
}
console.log('hidden safe credential checks passed');
