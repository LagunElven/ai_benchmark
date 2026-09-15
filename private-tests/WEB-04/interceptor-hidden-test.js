const { withSecurityHeaders } = require('./interceptor');

const original = {
  method: 'post',
  url: '/orders',
  headers: { authorization: 'old', 'x-csrf-token': 'old-csrf', Accept: 'json' },
};
const result = withSecurityHeaders(original, '  token-1  ', 'csrf-1');
if (original.headers.authorization !== 'old' || original.headers['x-csrf-token'] !== 'old-csrf') {
  throw new Error('input headers were mutated');
}
const authValues = Object.entries(result.headers)
  .filter(([name]) => name.toLowerCase() === 'authorization');
if (authValues.length !== 1 || authValues[0][1] !== 'Bearer token-1') {
  throw new Error('authorization replacement is incorrect');
}
const csrfValues = Object.entries(result.headers)
  .filter(([name]) => name.toLowerCase() === 'x-csrf-token');
if (csrfValues.length !== 1 || csrfValues[0][1] !== 'csrf-1') {
  throw new Error('CSRF replacement is incorrect');
}
const noCredentials = withSecurityHeaders({ method: 'DELETE', headers: {} }, ' ', '');
if (Object.keys(noCredentials.headers).length !== 0) throw new Error('blank tokens were added');
console.log('hidden interceptor checks passed');
