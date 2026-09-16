const { createOAuthRedirectHandler } = require('./oauth-deep-link');

function expectCode(action, expectedCode) {
  try {
    action();
  } catch (error) {
    if (error.code !== expectedCode) {
      throw new Error(`expected ${expectedCode}, received ${error.code}`);
    }
    return;
  }
  throw new Error(`expected ${expectedCode} rejection`);
}

const handler = createOAuthRedirectHandler('myapp://oauth/callback', 'state-123');
expectCode(() => handler.consume('myapp://other/callback?code=a&state=state-123'), 'invalid_redirect');
expectCode(() => handler.consume('https://oauth/callback?code=a&state=state-123'), 'invalid_redirect');
expectCode(() => handler.consume('myapp://oauth/callback?code=a&state=wrong'), 'state_mismatch');
expectCode(() => handler.consume('myapp://oauth/callback?error=access_denied&state=state-123'), 'oauth_error');
expectCode(() => handler.consume('myapp://oauth/callback?code=a&state=state-123#token=leaked'), 'invalid_redirect');
if (handler.consumed) throw new Error('failed callback was consumed');

const result = handler.consume(
  'myapp://oauth/callback?code=final%2Bcode&state=state-123&access_token=secret');
if (JSON.stringify(result) !== JSON.stringify({ code: 'final+code', state: 'state-123' })
    || !handler.consumed) {
  throw new Error('valid callback was not consumed safely');
}
expectCode(() => handler.consume('myapp://oauth/callback?code=again&state=state-123'), 'already_consumed');

const missing = createOAuthRedirectHandler('myapp://oauth/callback', 'state-123');
expectCode(() => missing.consume('myapp://oauth/callback?state=state-123'), 'invalid_redirect');
expectCode(() => missing.consume('myapp://oauth/callback?code=a'), 'invalid_redirect');
console.log('hidden OAuth deep-link checks passed');
