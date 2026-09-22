import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import PostCard from '../components/PostCard';


export default function FeedPage() {
  const[snippets,setSnippets]=useState([]);
  const[loading,setLoading]=useState(true);
  const[error,setError]=useState(null);
  const [language, setLanguage] = useState('All languages');

  useEffect(()=>{
    fetch('/api/snippets/')
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

  if (loading) return <p>Loading Snippets....</p>;
  if (error) return <p>Error:{error}</p>;

  return (
    <div className="feed-page">
      <section className="hero">
        <div>
          <p className="eyebrow">The developer’s little library</p>
          <h1>Share the snippet<br /><em>you’ll reuse tomorrow.</em></h1>
          <p className="hero-copy">Useful code, shared without the noise. Browse a growing collection of small solutions from the community.</p>
        </div>
        <Link className="button hero-button" to="/register">Join the community <span>→</span></Link>
      </section>
      <section className="feed-toolbar" aria-label="Feed controls">
        <div><h2>Latest snippets</h2><span>Small solutions shared by the community</span></div>
        <label className="filter-control">Filter by language
          <select value={language} onChange={(event) => setLanguage(event.target.value)}>
            {languages.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
      </section>
      {visiblePosts.length === 0 && <div className="empty-state"><h2>No snippets in this language yet.</h2><p>Try another filter.</p></div>}
      <div className="post-list">
        {visiblePosts.map((post) => <PostCard key={post.id} post={post} />)}
      </div>
    </div>
  );
}
