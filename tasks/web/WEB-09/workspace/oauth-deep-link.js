function createOAuthRedirectHandler(expectedRedirectUri, expectedState) {
  const consumed = false;
  return {
    consume(url) {
      const parsed = new URL(url);
      return { code: parsed.searchParams.get('code'), state: parsed.searchParams.get('state') };
    },
    get consumed() { return consumed; },
  };
}

module.exports = { createOAuthRedirectHandler };
