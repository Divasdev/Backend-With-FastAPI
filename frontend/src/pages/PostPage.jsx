import { useEffect, useState } from 'react';
import { Link, useParams,Navigate, useNavigate} from 'react-router-dom';

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString();
}


export default function PostPage() {
  const navigate=useNavigate()
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  function handleDelete(){
    if (!window.confirm('Delete this Snippet?'))
      return;
    fetch(`/api/snippets/${id}`,{
      method:'DELETE',
    })
    .then((res)=>{
      if (!res.ok) throw new Error('Failed to delete');
        navigate('/');
    })
    .catch((err)=>alert(err.message));
  }

  useEffect(() => {
    fetch(`/api/snippets/${id}`)
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

  if (loading) return <p>Loading...</p>;

  if (error || !post) {
    return (
      <div className="empty-state">
        <h2>Snippet not found.</h2>
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

      <div>
         <button
        className="button"
        style={{ background: '#e53e3e', marginTop: '1rem' }}
        onClick={handleDelete}
      >
        Delete Snippet
      </button>
      {/* Next to the delete button */}
      <Link className="button" to={`/posts/${id}/edit`}>Edit Snippet</Link>

      </div>
    </article>
  );
}