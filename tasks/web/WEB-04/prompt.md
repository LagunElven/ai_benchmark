# HTTP interceptor headers

Implement `withSecurityHeaders(request, bearerToken, csrfToken)`. Return a new request
object without mutating the input. Preserve URL, method and existing headers. Add
`Authorization: Bearer <token>` only when a non-blank bearer token is supplied. Add
`X-CSRF-Token` only for POST, PUT, PATCH or DELETE when a non-blank CSRF token is
supplied. Header names are case-insensitive for replacement, and an existing
Authorization/CSRF value must be replaced rather than duplicated. Keep the CommonJS
export and do not modify tests.
