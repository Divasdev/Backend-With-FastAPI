import { useAuth } from '../auth/AuthContext';
import { apiFetch } from '../api/api';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import PostCard from '../components/PostCard';


export default function FeedPage() {
  const { user } = useAuth();
  const[snippets,setSnippets]=useState([]);
  const[loading,setLoading]=useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const[error,setError]=useState(null);
  const [loadMoreError, setLoadMoreError] = useState(null);
  const [total, setTotal] = useState(0);
  const [languages, setLanguages] = useState([]);
  const [searchDraft, setSearchDraft] = useState('');
  const [search, setSearch] = useState('');
  const [language, setLanguage] = useState('');
  const [sort, setSort] = useState('new');
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

  useEffect(() => {
    let active = true;
    const params = new URLSearchParams({ sort, offset: '0', limit: '10' });
    if (search) params.set('q', search);
    if (language) params.set('language', language);

    setLoading(true);
    setError(null);
    apiFetch(`/api/snippets/?${params}`)
      .then((res) => res.json())
      .then((data) => {
        if (!active) return;
        setSnippets(data.items);
        setTotal(data.total);
        setLanguages((current) => [...new Set([...current, ...data.items.map((post) => post.language)])].sort());
        setLoading(false);
      })
      .catch((err) => {
        if (!active) return;
        setError(err.message);
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [language, search, sort]);

  function handleSearch(event) {
    event.preventDefault();
    setSearch(searchDraft.trim());
  }

  function loadMore() {
    const params = new URLSearchParams({ sort, offset: String(snippets.length), limit: '10' });
    if (search) params.set('q', search);
    if (language) params.set('language', language);

    setLoadingMore(true);
    setLoadMoreError(null);
    apiFetch(`/api/snippets/?${params}`)
      .then((res) => res.json())
      .then((data) => {
        setSnippets((current) => [...current, ...data.items]);
        setTotal(data.total);
        setLanguages((current) => [...new Set([...current, ...data.items.map((post) => post.language)])].sort());
      })
      .catch((err) => setLoadMoreError(err.message))
      .finally(() => setLoadingMore(false));
  }

  if (loading) return <p className="page-loader" role="status">Loading snippets...</p>;
  if (error) {
    return (
      <div className="empty-state">
        <h1 style={{ color: '#dc2626', fontSize: '2.5rem', fontWeight: 'bold', margin: '0 0 12px 0' }}>FUCK YOU RENDER</h1>
        <h2>Could not load snippets.</h2>
        <p role="alert">{error}</p>
        <button type="button" className="button" onClick={() => window.location.reload()}>Try again</button>
      </div>
    );
  }

  return (
    <div className="feed-page">
      <div style={{ background: '#fee2e2', border: '2px solid #ef4444', color: '#991b1b', padding: '14px 20px', borderRadius: '8px', marginBottom: '20px', fontWeight: '800', fontSize: '1.5rem', textAlign: 'center', letterSpacing: '1px' }}>
        🔥 FUCK YOU RENDER 🔥
      </div>
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
        <form className="feed-filters" onSubmit={handleSearch}>
          <label className="search-control">Search snippets
            <input type="search" value={searchDraft} onChange={(event) => setSearchDraft(event.target.value)} placeholder="Title or description" />
          </label>
          <label className="filter-control">Filter by language
            <select value={language} onChange={(event) => setLanguage(event.target.value)}>
              <option value="">All languages</option>
              {languages.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label className="filter-control">Sort by
            <select value={sort} onChange={(event) => setSort(event.target.value)}>
              <option value="new">Newest</option>
              <option value="top">Top voted</option>
            </select>
          </label>
          <button className="button small-button" type="submit">Search</button>
        </form>
      </section>
      {snippets.length === 0 && <div className="empty-state">
        <h2>{search || language || sort === 'top' ? 'No matching snippets.' : 'No snippets yet.'}</h2>
        <p>{search || language || sort === 'top' ? 'Try changing your search or filters.' : user ? 'Be the first to share one.' : 'Create an account to share the first one.'}</p>
        <Link className="button" to={user ? "/create" : "/register"}>{user ? "Share a snippet" : "Join the community"}</Link>
      </div>}
      {voteError && <p className="notice error" role="alert">{voteError}</p>}
      <div className="post-list">
        {snippets.map((post) => <PostCard key={post.id} post={post} myVote={myVotes[post.id]} onVote={handleVote} />)}
      </div>
      {loadMoreError && <p className="notice error" role="alert">{loadMoreError}</p>}
      {snippets.length < total && <div className="pagination-actions">
        <button type="button" className="secondary-button" onClick={loadMore} disabled={loadingMore}>
          {loadingMore ? 'Loading…' : 'Load more'}
        </button>
        <span>Showing {snippets.length} of {total} snippets</span>
      </div>}
    </div>
  );
}
