
import { Link, useNavigate } from 'react-router-dom';
import { registerAccount } from '../api/register';
import ProfileImagePicker from '../components/ProfileImagePicker';
import { useAuth } from '../auth/AuthContext';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { setNotice } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [profileImage, setProfileImage] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setError(null);

    try {
      await registerAccount({ ...form, profileImage });

      setNotice(profileImage
        ? 'Account created successfully. Your photo was previewed but not saved. Log in with your email and password.'
        : 'Account created successfully. Log in with your email and password.');
      navigate('/login');
    } catch (error) {
      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-card">
        <p className="eyebrow">Make it useful</p>
        <h1>Join SnipShare</h1>
        <p className="auth-intro">Create an account to share your own snippets.</p>
        {error && <p className="notice error" role="alert">{error}</p>}
        <form onSubmit={handleSubmit} className="form-stack" aria-busy={submitting}>
          <ProfileImagePicker file={profileImage} onChange={setProfileImage} email={form.email} disabled={submitting} />
          <label>Email address<input required type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password (at least 8 characters)<input required minLength="8" type="password" autoComplete="new-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
          <button className="button full-width" disabled={submitting}>{submitting && <span className="button-spinner" aria-hidden="true" />}{submitting ? 'Creating account...' : 'Create account'}</button>
        </form>
        <p className="auth-switch">Already a member? <Link to="/login">Log in</Link></p>
      </div>
    </section>
  );
}
