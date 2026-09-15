const { withSecurityHeaders } = require('../interceptor');

const original = { method: 'GET', url: '/orders', headers: { Accept: 'json' } };
const result = withSecurityHeaders(original, 'abc', 'csrf');
if (result === original || result.headers.Authorization !== 'Bearer abc') {
  throw new Error('bearer header was not added immutably');
}
if (result.headers['X-CSRF-Token'] !== undefined) throw new Error('GET received CSRF header');
console.log('public interceptor checks passed');
