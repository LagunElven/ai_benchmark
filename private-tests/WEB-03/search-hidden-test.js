'use strict';

const assert = require('node:assert/strict');
const { searchLatest } = require('./search');

const seen = [];
const pending = searchLatest((query) => {
  if (query === 'latest') return Promise.resolve('LATEST');
  return new Promise((resolve) => setTimeout(() => resolve(query), 5));
}, ['stale', 'latest'], (result) => seen.push(result));

pending.then(() => {
  assert.deepEqual(seen, ['LATEST']);
  console.log('hidden switchMap checks passed');
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
