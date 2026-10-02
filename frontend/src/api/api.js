export const API_URL = "http://localhost:8000";

export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const clearToken = () => localStorage.removeItem("token");

export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;   // ← the wristband

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (res.status === 401) clearToken();   // token expired or bad → forget it
  return res;
}