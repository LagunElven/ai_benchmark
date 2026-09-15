const { readFirst } = require('../observable');

readFirst(42).then((value) => {
  if (value !== 42) throw new Error('scalar value changed');
  console.log('public observable checks passed');
});
