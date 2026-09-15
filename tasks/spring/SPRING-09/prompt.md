# Bearer and CSRF authorization

Implement `RequestAuthorizer.isAllowed`. Require an exact `Authorization: Bearer <token>`
header for every request. For POST, PUT, PATCH and DELETE, also require an exact
`X-CSRF-Token` header matching the supplied CSRF token. GET and HEAD do not require
CSRF. Header names are case-insensitive; blank/missing tokens, null requests and
unknown methods are denied. Never mutate the request headers.
