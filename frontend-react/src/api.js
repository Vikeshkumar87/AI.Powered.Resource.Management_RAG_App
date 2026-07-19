const API_BASE = '/api/v1';

export async function api(path, options = {}) {
  let session = null;
  try {
    const sessionRaw = localStorage.getItem('arm_auth_session');
    session = sessionRaw ? JSON.parse(sessionRaw) : null;
  } catch {
    session = null;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      'X-User-Role': session?.role || 'user',
      'X-User-Name': session?.username || '',
      ...(options.headers || {}),
    },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}
