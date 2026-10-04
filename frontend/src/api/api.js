export const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
export const getToken = () => localStorage.getItem('token');
export const setToken = (token) => localStorage.setItem('token', token);
export const clearToken = () => {
  localStorage.removeItem('token');
  window.dispatchEvent(new Event('auth-cleared'));
};

export async function apiFetch(path, options = {}) {
  const { anonymous = false, ...request } = options;
  const headers = new Headers(request.headers);
  const token = anonymous ? null : getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { ...request, headers });
  } catch {
    throw new Error('Could not reach the server. Check that the backend is running.');
  }
  if (res.status === 401 && token && token === getToken()) clearToken();
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => `${item.loc?.at(-1) || 'Field'}: ${item.msg}`).join('; ')
      : data.detail;
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${res.status}). Please try again.`);
  }
  return res;
}
