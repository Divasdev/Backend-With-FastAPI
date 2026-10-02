import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { API_URL, setToken } from '../api/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      // FastAPI's login endpoint expects form data and calls the email field "username".
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: form.email, password: form.password }),
      });

      if (!res.ok) {
        setError(res.status === 401 ? 'Incorrect email or password' : 'Something went wrong. Please try again.');
        setSubmitting(false);
        return;
      }

      const data = await res.json();
      setToken(data.access_token);   // save the wristband
      navigate('/');
    } catch {
      setError('Could not reach the server. Is the backend running?');
      setSubmitting(false);
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">Welcome back</p>
        <h1>Log in to SnipShare</h1>
        <p className="auth-intro">Use the email and password you registered with.</p>
        {error && <p className="notice error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit} className="form-stack">
          <label>Email address<input required type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input required type="password" autoComplete="current-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="button full-width" disabled={submitting}>{submitting ? 'Logging in...' : 'Log in'}</button>
        </form>
        <p className="auth-switch">New here? <Link to="/register">Create an account</Link></p>
      </div>
    </section>
  );
}
