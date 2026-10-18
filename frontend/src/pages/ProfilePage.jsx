import { useAuth } from '../auth/AuthContext';
import { apiFetch } from '../api/api';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import Avatar from '../components/Avatar';
import PostCard from '../components/PostCard';

function formatJoined(value) {
  return new Date(value).toLocaleDateString('en', { month: 'long', year: 'numeric' });
}

export default function ProfilePage() {
  const { user } = useAuth();
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [snippets, setSnippets] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [loadMoreError, setLoadMoreError] = useState(null);
  // Same vote handling as the feed: { snippetId: 1 or -1 }.
  const [myVotes, setMyVotes] = useState({});
  const [voteError, setVoteError] = useState(null);

  useEffect(() => {
    // Load the user and their snippets together.
    Promise.all([
      apiFetch(`/users/${userId}`).then((res) => res.json()),
      apiFetch(`/api/snippets/?owner_id=${userId}&offset=0&limit=10`).then((res) => res.json()),
    ])
      .then(([profileData, snippetData]) => {
        setProfile(profileData);
        setSnippets(snippetData.items);
        setTotal(snippetData.total);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [userId]);

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

  function loadMore() {
    setLoadingMore(true);
    setLoadMoreError(null);
    apiFetch(`/api/snippets/?owner_id=${userId}&offset=${snippets.length}&limit=10`)
      .then((res) => res.json())
      .then((data) => {
        setSnippets((current) => [...current, ...data.items]);
        setTotal(data.total);
      })
      .catch((err) => setLoadMoreError(err.message))
      .finally(() => setLoadingMore(false));
  }

  if (loading) return <p className="page-loader" role="status">Loading profile...</p>;

  if (error || !profile) {
    return (
      <div className="empty-state">
        <h2>Could not load this profile.</h2>
        <p role="alert">{error || 'User not found.'}</p>
        <Link className="button" to="/">
          Back to feed
        </Link>
      </div>
    );
  }

  return (
    <div className="detail-page">
      <Link className="back-link" to="/">
        ← All snippets
      </Link>

      <section className="profile-header">
        <Avatar src={profile.profile_image_url} email={profile.email} large />
        <div>
          <h1>{profile.email}</h1>
          <p>
            Joined {formatJoined(profile.created_at)} · {total} {total === 1 ? 'snippet' : 'snippets'}
          </p>
        </div>
      </section>

      {snippets.length === 0 && <div className="empty-state"><h2>No snippets yet.</h2></div>}
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
