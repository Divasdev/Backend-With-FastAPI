import { useAuth } from '../auth/AuthContext';
import { Link, NavLink, Outlet } from 'react-router-dom';

export default function Layout() {
  const { user, loading, logout, notice, setNotice, sessionError, retrySession } = useAuth();
  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="header-content">
          <Link className="brand" to="/" aria-label="SnipShare home">
            <span className="brand-mark">&lt;/&gt;</span>
            <span>SnipShare</span>
          </Link>
          <nav className="main-nav" aria-label="Main navigation">
            <NavLink to="/" end>Explore</NavLink>
          </nav>
          <div className="auth-nav">
            {loading ? <span role="status">Checking session...</span> : user ? <>
              <span className="account-label">Signed in as {user.email}</span>
              <NavLink to="/create">Share Snippet</NavLink>
              <button className="button small-button" onClick={logout}>Log out</button>
            </> : <>
              <NavLink to="/login">Log in</NavLink>
              <NavLink className="button small-button" to="/register">Join SnipShare</NavLink>
            </>}

          </div>
        </div>
      </header>
      <main className="page-content">
        {notice && <div className="notice success" role="status">{notice} <button onClick={() => setNotice('')} aria-label="Dismiss notification">×</button></div>}
        {sessionError && <div className="notice error" role="alert">{sessionError} <button onClick={retrySession}>Retry session</button></div>}
        <Outlet />
      </main>
      <footer className="site-footer">Built for sharing small, useful pieces of code.</footer>
    </div>
  );
}
