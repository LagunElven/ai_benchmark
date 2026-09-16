function withSafeCredentials(request, bearerToken, csrfToken, origin) {
  if (!request || typeof request !== 'object') throw new TypeError('request is required');
  const securityHeaders = new Set(['authorization', 'x-csrf-token']);
  const headers = {};
  for (const [name, value] of Object.entries(request.headers || {})) {
    if (!securityHeaders.has(name.toLowerCase())) headers[name] = value;
  }

  let sameOrigin = false;
  try {
    const base = new URL(origin);
    sameOrigin = new URL(request.url || '', base).origin === base.origin;
  } catch (_) {
    sameOrigin = false;
  }
  const method = String(request.method || 'GET').toUpperCase();
  const token = typeof bearerToken === 'string' ? bearerToken.trim() : '';
  const csrf = typeof csrfToken === 'string' ? csrfToken.trim() : '';
  if (sameOrigin && token) headers.Authorization = `Bearer ${token}`;
  if (sameOrigin && new Set(['POST', 'PUT', 'PATCH', 'DELETE']).has(method) && csrf) {
    headers['X-CSRF-Token'] = csrf;
  }
  return { ...request, headers };
}

module.exports = { withSafeCredentials };
