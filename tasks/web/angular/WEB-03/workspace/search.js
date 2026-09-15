'use strict';

async function searchLatest(api, queries, onResult) {
  let latest = 0;
  const pending = queries.map((query) => {
    const ticket = ++latest;
    return Promise.resolve().then(() => api(query)).then((result) => {
      if (ticket === latest) {
        onResult(result);
      }
      return result;
    });
  });
  return Promise.all(pending);
}

module.exports = { searchLatest };
