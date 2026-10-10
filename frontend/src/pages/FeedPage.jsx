import { useAuth } from '../auth/AuthContext';
import { apiFetch } from '../api/api';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PostCard from '../components/PostCard';


export default function FeedPage() {
  const { user } = useAuth();
  const[snippets,setSnippets]=useState([]);
  const[loading,setLoading]=useState(true);
  const[error,setError]=useState(null);
  const [language, setLanguage] = useState('All languages');
  // My votes as { snippetId: 1 or -1 }, so each card knows which arrow to highlight.
  const [myVotes, setMyVotes] = useState({});
  const [voteError, setVoteError] = useState(null);

  useEffect(() => {
    if (!user) {
      setMyVotes({});
      return;
    }
    apiFetch('/users/me/votes')
      .then((res) => res.json())
      .then((data) => setMyVotes(Object.fromEntries(data.map((vote) => [vote.snip_id, vote.value]))))
      .catch((err) => setVoteError(err.message));
  }, [user]);

  function handleVote(snipId, value) {
    // Clicking the arrow I already chose removes my vote; anything else sets it.
    const remove = myVotes[snipId] === value;
    const options = remove
      ? { method: 'DELETE' }
      : { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ value }) };
    setVoteError(null);
    apiFetch(`/api/snippets/${snipId}/vote`, options)
      .then((res) => res.json())
      .then((updated) => {
        setSnippets((list) => list.map((post) => (post.id === updated.id ? updated : post)));
        setMyVotes((votes) => ({ ...votes, [snipId]: remove ? undefined : value }));
      })
      .catch((err) => setVoteError(err.message));
  }

  useEffect(()=>{
    apiFetch('/api/snippets/')
    .then((res)=>{
      if (!res.ok) throw new Error("Failed to Fetch Snippets");
        return res.json();
      
    })
    .then((data)=>{
      setSnippets(data);
      setLoading(false);
    })
    .catch((err)=>{
      setError(err.message);
      setLoading(false);
    });
  },[]);


  const languages = useMemo(
    () => ['All languages', ...new Set(snippets.map((post) => post.language).sort())],
    [snippets],
  );
  const visiblePosts = language === 'All languages' ? snippets : snippets.filter((post) => post.language === language);

  if (loading) return <p className="page-loader" role="status">Loading snippets...</p>;
  if (error) {
    return (
      <div className="empty-state">
        <h2>Could not load snippets.</h2>
        <p role="alert">{error}</p>
        <button type="button" className="button" onClick={() => window.location.reload()}>Try again</button>
      </div>
    );
  }

  return (
    <div className="feed-page">
      <section className="hero">
        <div>
          <p className="eyebrow">{user ? `Welcome, ${user.email.split('@')[0]}` : 'The developer’s little library'}</p>
          <h1>Share the snippet<br /><em>you’ll reuse tomorrow.</em></h1>
          <p className="hero-copy">Useful code, shared without the noise. Browse a growing collection of small solutions from the community.</p>
        </div>
        <Link className="button hero-button" to={user ? "/create" : "/register"}>{user ? "Share a snippet" : "Join the community"} <span>→</span></Link>
      </section>
      <section className="feed-toolbar" aria-label="Feed controls">
        <div><h2>Latest snippets</h2><span>Small solutions shared by the community</span></div>
        {snippets.length > 0 && <label className="filter-control">Filter by language
          <select value={language} onChange={(event) => setLanguage(event.target.value)}>
            {languages.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>}
      </section>
      {snippets.length === 0 && <div className="empty-state">
        <h2>No snippets yet.</h2>
        <p>{user ? 'Be the first to share one.' : 'Create an account to share the first one.'}</p>
        <Link className="button" to={user ? "/create" : "/register"}>{user ? "Share a snippet" : "Join the community"}</Link>
      </div>}
      {snippets.length > 0 && visiblePosts.length === 0 && <div className="empty-state"><h2>No snippets in this language yet.</h2><p>Try another filter.</p></div>}
      {voteError && <p className="notice error" role="alert">{voteError}</p>}
      <div className="post-list">
        {visiblePosts.map((post) => <PostCard key={post.id} post={post} myVote={myVotes[post.id]} onVote={handleVote} />)}
      </div>
    </div>
  );
}
