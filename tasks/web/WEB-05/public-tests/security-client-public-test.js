const { withSafeCredentials } = require('../security-client');

const original = { method: 'POST', url: '/orders', headers: { Accept: 'json' } };
const result = withSafeCredentials(original, 'abc', 'csrf', 'https://app.example.test');
if (result === original || result.headers === original.headers) throw new Error('request mutated');
if (result.headers.Authorization !== 'Bearer abc' || result.headers['X-CSRF-Token'] !== 'csrf') {
  throw new Error('security headers were not attached');
}
if (original.headers.Authorization || original.headers['X-CSRF-Token']) {
  throw new Error('source headers changed');
}
console.log('public safe credential checks passed');
