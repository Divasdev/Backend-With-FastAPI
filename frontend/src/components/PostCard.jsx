import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

function formatDate(value) {
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

export default function PostCard({ post, myVote, onVote }) {
  const { user } = useAuth();
  return (
    <article className="post-card">
      <div className="vote-stack" aria-label={`${post.vote_count} votes`}>
        <button type="button" className={myVote === 1 ? 'active' : ''} onClick={() => onVote(post.id, 1)} disabled={!user} aria-label="Upvote" aria-pressed={myVote === 1}>▲</button>
        <strong>{post.vote_count}</strong>
        <button type="button" className={myVote === -1 ? 'active' : ''} onClick={() => onVote(post.id, -1)} disabled={!user} aria-label="Downvote" aria-pressed={myVote === -1}>▼</button>
      </div>
      <div className="post-card-main">
        <div className="post-card-meta"><span className="language-pill">{post.language}</span><span>{formatDate(post.created_at)}</span>{user?.id === post.owner_id && <span className="owner-pill">Your snippet</span>}</div>
        <h2><Link to={`/posts/${post.id}`}>{post.title}</Link></h2>
        {post.description && <p>{post.description}</p>}
        <pre><code>{post.code}</code></pre>
        <Link className="read-link" to={`/posts/${post.id}`}>View snippet <span>→</span></Link>
      </div>
    </article>
  );
}
