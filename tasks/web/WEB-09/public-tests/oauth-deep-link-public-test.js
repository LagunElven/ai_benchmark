const { createOAuthRedirectHandler } = require('../oauth-deep-link');

const handler = createOAuthRedirectHandler('myapp://oauth/callback', 'state-123');
const result = handler.consume('myapp://oauth/callback?code=abc%20123&state=state-123');
if (JSON.stringify(result) !== JSON.stringify({ code: 'abc 123', state: 'state-123' })) {
  throw new Error('OAuth callback was not decoded');
}
console.log('public OAuth deep-link checks passed');
