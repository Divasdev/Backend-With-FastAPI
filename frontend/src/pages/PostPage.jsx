import { useAuth } from '../auth/AuthContext';
import { apiFetch } from '../api/api';
import { useEffect, useState } from 'react';
import { Link, useParams, useNavigate} from 'react-router-dom';

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString();
}


export default function PostPage() {
  const { user, setNotice } = useAuth();
  const navigate=useNavigate()
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  async function handleDelete() {
    if (deleting) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await apiFetch(`/api/snippets/${id}`, { method: 'DELETE' });
      setNotice('Snippet deleted. It has been removed from the feed.');
      navigate('/');
    } catch (error) {
      setDeleteError(error.message);
    } finally {
      setDeleting(false);
    }
  }

  useEffect(() => {
    apiFetch(`/api/snippets/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error('Snippet not found');
        return res.json();
      })
      .then((data) => {
        setPost(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <p className="page-loader" role="status">Loading snippet...</p>;

  if (error || !post) {
    return (
      <div className="empty-state">
        <h2>Could not load this snippet.</h2>
        <p role="alert">{error || 'Snippet not found.'}</p>
        <Link className="button" to="/">
          Back to feed
        </Link>
      </div>
    );
  }

  return (
    <article className="detail-page">
      <Link className="back-link" to="/">
        ← All snippets
      </Link>

      <div className="detail-header">
        <div>
          <div className="post-card-meta">
            <span className="language-pill">{post.language}</span>
            <span>Shared {formatDate(post.created_at)}</span>
          </div>

          <h1>{post.title}</h1>

          {post.description && <p>{post.description}</p>}
        </div>
      </div>

      <div className="code-panel">
        <div className="code-panel-bar">
          <span>{post.language}</span>
          <span>snippet</span>
        </div>

        <pre>
          <code>{post.code}</code>
        </pre>
      </div>

      {user?.id === post.owner_id && <div className="detail-actions">
        {confirmDelete ? <section className="delete-confirmation" aria-labelledby="delete-heading" aria-busy={deleting}>
          <h2 id="delete-heading">Delete this snippet?</h2>
          <p>“{post.title}” will be permanently removed. This cannot be undone.</p>
          {deleteError && <p className="notice error" role="alert">{deleteError}</p>}
          <div className="form-actions">
            <button type="button" className="secondary-button" autoFocus disabled={deleting} onClick={() => setConfirmDelete(false)}>Keep snippet</button>
            <button type="button" className="danger-button" disabled={deleting} onClick={handleDelete}>
              {deleting && <span className="button-spinner" aria-hidden="true" />}
              {deleting ? 'Deleting...' : 'Yes, delete snippet'}
            </button>
          </div>
        </section> : <div className="owner-actions">
          <Link className="button" to={`/posts/${id}/edit`}>Edit snippet</Link>
          <button type="button" className="danger-button" onClick={() => { setDeleteError(''); setConfirmDelete(true); }}>Delete snippet</button>
        </div>}
      </div>}

    </article>
  );
}