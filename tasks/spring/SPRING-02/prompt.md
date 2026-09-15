# Stable REST exception mapping

Implement `ApiErrorMapper.toResponse`. Map `NotFoundException` to HTTP 404/code
`not_found`, `IllegalArgumentException` to HTTP 400/code `invalid_request`, and every
other failure (including `null`) to HTTP 500/code `internal_error`. The response message
for an unexpected failure must be the generic `Internal server error`, never the
exception's secret message. Preserve the public nested types and do not add Spring
dependencies or modify tests.
