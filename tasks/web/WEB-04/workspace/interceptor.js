function withSecurityHeaders(request, bearerToken, csrfToken) {
  const headers = request.headers || {};
  headers.Authorization = `Bearer ${bearerToken}`;
  headers['X-CSRF-Token'] = csrfToken;
  return { ...request, headers };
}

module.exports = { withSecurityHeaders };
