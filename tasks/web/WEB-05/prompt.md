# Safe HTTP credentials

Implement `withSafeCredentials(request, bearerToken, csrfToken, origin)`. Return a new
request and a new headers object; never mutate the request or its headers. Treat header
names case-insensitively and leave at most one canonical security header of each kind.

For a relative URL or an absolute URL with the same origin as `origin`, attach
`Authorization: Bearer <trimmed token>` when the bearer token is nonblank. Attach
`X-CSRF-Token: <trimmed token>` only for POST, PUT, PATCH and DELETE requests and only
when the CSRF token is nonblank. GET, HEAD and OPTIONS do not receive CSRF. Remove stale
security headers when a credential is unavailable or the request is cross-origin, so
credentials cannot be leaked. Preserve all unrelated headers and request fields.
