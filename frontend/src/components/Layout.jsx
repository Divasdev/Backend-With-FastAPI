import { useCallback } from 'react';
import Toast from './Toast';
import Avatar from './Avatar';
import { useAuth } from '../auth/AuthContext';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';

export default function Layout() {
  const { user, loading, logout, notice, setNotice, sessionError, retrySession } = useAuth();
  const navigate = useNavigate();
  const dismissNotice = useCallback(() => setNotice(''), [setNotice]);

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className={`header-content${user ? ' signed-in' : ''}`}>
          <Link className="brand" to="/" aria-label="SnipShare home">
            <span className="brand-mark">&lt;/&gt;</span>
            <span>SnipShare</span>
          </Link>
          <nav className="main-nav" aria-label="Main navigation">
            <NavLink to="/" end>Explore</NavLink>
          </nav>
          <div className="auth-nav">
            {loading ? <span role="status">Checking session...</span> : user ? <>
              <NavLink className="button small-button" to="/create">Share snippet</NavLink>
              <span className="account-identity" title={`Logged in as ${user.email}`}>
                <Avatar key={`${user.id}:${user.profile_image_url || ''}`} src={user.profile_image_url} email={user.email} />
                <span className="account-label">
                  <span className="account-status">Logged in</span>
                  <span className="account-email">{user.email}</span>
                </span>
              </span>
              <button type="button" className="secondary-button small-button" onClick={handleLogout}>Log out</button>
            </> : <>
              <span className="account-status signed-out">Not logged in</span>
              <NavLink to="/login">Log in</NavLink>
              <NavLink className="button small-button" to="/register">Join SnipShare</NavLink>
            </>}

          </div>
        </div>
      </header>
      <main className="page-content">

        {sessionError && <div className="notice error" role="alert">{sessionError} <button onClick={retrySession}>Retry session</button></div>}
        <Outlet />
      </main>
      <Toast message={notice} onDismiss={dismissNotice} />
      <footer className="site-footer">Built for sharing small, useful pieces of code.</footer>
    </div>
  );
}
