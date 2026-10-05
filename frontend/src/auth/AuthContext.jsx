import { createContext, useContext, useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { apiFetch, clearToken, getToken, setToken } from '../api/api';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState('');
  const [sessionError, setSessionError] = useState('');
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    const reset = () => {
      setUser(null);
      setNotice('Your session ended. Please log in again.');
    };
    const restore = async () => {
      setLoading(true);
      setSessionError('');
      try {
        const token = getToken();
        const profile = token ? await (await apiFetch('/users/me')).json() : null;
        if (active && token === getToken()) setUser(profile);
      } catch (error) {
        if (active) setSessionError(getToken() ? error.message : '');
      } finally {
        if (active) setLoading(false);
      }
    };
    window.addEventListener('auth-cleared', reset);
    window.addEventListener('storage', restore);
    restore();
    return () => {
      active = false;
      window.removeEventListener('auth-cleared', reset);
      window.removeEventListener('storage', restore);
    };
  }, [retry]);

  async function login(email, password) {
    const res = await apiFetch('/auth/login', {
      anonymous: true,
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email.trim(), password }),
    });
    const data = await res.json();
    setToken(data.access_token);
    try {
      const profile = await (await apiFetch('/users/me')).json();
      setUser(profile);
      setSessionError('');
      setNotice(`You're logged in as ${profile.email}.`);
    } catch (error) {
      clearToken();
      setNotice('');
      throw error;
    }
  }

  function logout() {
    clearToken();
    setSessionError('');
    setNotice('You have been logged out.');
  }

  return <AuthContext.Provider value={{ user, loading, login, logout, notice, setNotice, sessionError, retrySession: () => setRetry((value) => value + 1) }}>{children}</AuthContext.Provider>;
}

export function RequireAuth({ children }) {
  const { user, loading, sessionError } = useAuth();
  const location = useLocation();
  if (loading) return <p className="page-loader" role="status">Checking your session...</p>;
  // Layout already shows the session error with a retry button above this page.
  if (sessionError) return null;
  return user ? children : <Navigate to="/login" replace state={{ from: location.pathname }} />;
}

// Login and register are for visitors. Someone already logged in is sent on,
// so they never see a login form while the header says they have an account.
export function GuestOnly({ children }) {
  const { user } = useAuth();
  const location = useLocation();
  return user ? <Navigate to={location.state?.from || '/'} replace /> : children;
}
