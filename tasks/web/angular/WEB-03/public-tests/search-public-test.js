'use strict';

const assert = require('node:assert/strict');
const { searchLatest } = require('../search');

const delays = { a: 40, ab: 20, abc: 1 };
const seen = [];
searchLatest((query) => new Promise((resolve) => {
  setTimeout(() => resolve(query.toUpperCase()), delays[query]);
}), ['a', 'ab', 'abc'], (result) => seen.push(result)).then(() => {
  assert.deepEqual(seen, ['ABC']);
  console.log('public switchMap checks passed');
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
