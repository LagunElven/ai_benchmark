# OAuth callback from a Capacitor deep link

Implement `createOAuthRedirectHandler(expectedRedirectUri, expectedState)`. It returns
an object with `consume(url)` and a read-only `consumed` property. `consume` must accept
one callback only when the URL has the same protocol, host, port and path as the expected
redirect URI, has no fragment, and contains nonblank `code` and `state` query parameters.
The state must exactly equal the expected state. Decode query parameters using the URL
standard and return exactly `{code, state}`.

Reject malformed or foreign URLs with an error whose `code` is `invalid_redirect`, reject
an OAuth `error` response with `code` `oauth_error`, reject a state mismatch with
`code` `state_mismatch`, and reject a second successful consumption with
`code` `already_consumed`. Failed attempts must not consume the handler. Never return
tokens or arbitrary query parameters, and do not modify the tests.
