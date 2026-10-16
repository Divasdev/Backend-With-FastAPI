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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Same vote handling as the feed: { snippetId: 1 or -1 }.
  const [myVotes, setMyVotes] = useState({});
  const [voteError, setVoteError] = useState(null);

  useEffect(() => {
    // Load the user and their snippets together.
    Promise.all([
      apiFetch(`/users/${userId}`).then((res) => res.json()),
      apiFetch(`/api/snippets/?owner_id=${userId}`).then((res) => res.json()),
    ])
      .then(([profileData, snippetData]) => {
        setProfile(profileData);
        setSnippets(snippetData);
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
            Joined {formatJoined(profile.created_at)} · {snippets.length} {snippets.length === 1 ? 'snippet' : 'snippets'}
          </p>
        </div>
      </section>

      {snippets.length === 0 && <div className="empty-state"><h2>No snippets yet.</h2></div>}
      {voteError && <p className="notice error" role="alert">{voteError}</p>}
      <div className="post-list">
        {snippets.map((post) => <PostCard key={post.id} post={post} myVote={myVotes[post.id]} onVote={handleVote} />)}
      </div>
    </div>
  );
}
