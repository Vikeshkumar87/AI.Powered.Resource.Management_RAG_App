const API_BASE = '/api/v1';

export async function api(path, options = {}) {
  let session = null;
  try {
    const sessionRaw = localStorage.getItem('arm_auth_session');
    session = sessionRaw ? JSON.parse(sessionRaw) : null;
  } catch {
    session = null;
  }

  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
  const headers = {
    ...(session?.token ? { Authorization: `Bearer ${session.token}` } : {}),
    'X-User-Role': session?.role || 'user',
    'X-User-Name': session?.username || '',
    ...(options.headers || {}),
  };

  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}
