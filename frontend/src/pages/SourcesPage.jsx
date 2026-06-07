import { useState } from 'react'
import { Search, ExternalLink, MessageCircle, Heart, BookOpen, Clock, Star, GitFork, Eye } from 'lucide-react'
import { sources } from '../api'

const TABS = [
  { id: 'gitlab',     label: 'GitLab' },
  { id: 'reddit',     label: 'Reddit' },
  { id: 'hackernews', label: 'Hacker News' },
  { id: 'x',          label: 'X / Twitter' },
  { id: 'devto',      label: 'Dev.to' },
]

function timeAgo(ts) {
  if (!ts) return ''
  const now = Date.now() / 1000
  const s = typeof ts === 'number' ? ts : new Date(ts).getTime() / 1000
  const d = now - s
  if (d < 60) return 'just now'
  if (d < 3600) return `${Math.floor(d / 60)}m ago`
  if (d < 86400) return `${Math.floor(d / 3600)}h ago`
  return `${Math.floor(d / 86400)}d ago`
}

// ── GitLab ─────────────────────────────────────────────
function GitLabTab() {
  const [username, setUsername] = useState('')
  const [projects, setProjects] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load() {
    if (!username.trim()) return
    setLoading(true); setError(null); setProjects(null)
    try {
      const data = await sources.gitlab.userProjects(username)
      setProjects(data)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell
      username={username} setUsername={setUsername}
      onSearch={load} loading={loading} error={error}
      placeholder="gitlab username"
    >
      {projects?.projects?.length > 0 && (
        <>
          <div className="panel-title" style={{ marginBottom: 10 }}>
            PROJECTS ({projects.count})
          </div>
          <div className="card-grid">
            {projects.projects.map((p, i) => (
              <div className="source-card" key={i}>
                <div className="source-card-name">
                  <a href={p.url} target="_blank" rel="noreferrer">{p.full_name || p.name}</a>
                </div>
                <div className="source-card-desc">{p.description || <span className="muted-italic">No description</span>}</div>
                <div className="source-card-meta">
                  <span><Star size={11} /> {p.stargazers_count}</span>
                  <span><GitFork size={11} /> {p.forks_count}</span>
                  {p.language && <span className="tag">{p.language}</span>}
                  {p.topics?.slice(0, 3).map((t, j) => <span className="tag tag-blue" key={j}>{t}</span>)}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </SourceTabShell>
  )
}

// ── Reddit ─────────────────────────────────────────────
function RedditTab() {
  const [username, setUsername] = useState('')
  const [userInfo, setUserInfo] = useState(null)
  const [posts, setPosts] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load() {
    if (!username.trim()) return
    setLoading(true); setError(null); setUserInfo(null); setPosts(null)
    try {
      const [u, p] = await Promise.all([
        sources.reddit.user(username),
        sources.reddit.submissions(username),
      ])
      setUserInfo(u); setPosts(p)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell
      username={username} setUsername={setUsername}
      onSearch={load} loading={loading} error={error}
      placeholder="reddit username"
    >
      {userInfo && (
        <div className="stat-grid" style={{ marginBottom: 16 }}>
          <div className="stat-box">
            <div className="stat-val">{userInfo.link_karma?.toLocaleString()}</div>
            <div className="stat-label">Link Karma</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.comment_karma?.toLocaleString()}</div>
            <div className="stat-label">Comment Karma</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.subreddit || '—'}</div>
            <div className="stat-label">Primary Subreddit</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.is_gold ? 'YES' : 'NO'}</div>
            <div className="stat-label">Gold</div>
          </div>
        </div>
      )}
      {posts?.posts?.length > 0 && (
        <>
          <div className="panel-title" style={{ marginBottom: 10 }}>RECENT POSTS ({posts.count})</div>
          <div className="card-grid">
            {posts.posts.map((p, i) => (
              <div className="source-card" key={i}>
                <div className="source-card-name">
                  <a href={p.permalink} target="_blank" rel="noreferrer">{p.title}</a>
                </div>
                <div className="source-card-desc">
                  <span className="tag tag-red">{p.subreddit}</span>
                </div>
                <div className="source-card-meta">
                  <span><Heart size={11} /> {p.score}</span>
                  <span><MessageCircle size={11} /> {p.num_comments}</span>
                  <span><Clock size={11} /> {timeAgo(p.created_utc)}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </SourceTabShell>
  )
}

// ── Hacker News ─────────────────────────────────────────
function HackerNewsTab() {
  const [username, setUsername] = useState('')
  const [userInfo, setUserInfo] = useState(null)
  const [submissions, setSubmissions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load() {
    if (!username.trim()) return
    setLoading(true); setError(null); setUserInfo(null); setSubmissions(null)
    try {
      const [u, s] = await Promise.all([
        sources.hackernews.user(username),
        sources.hackernews.submissions(username),
      ])
      setUserInfo(u); setSubmissions(s)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell
      username={username} setUsername={setUsername}
      onSearch={load} loading={loading} error={error}
      placeholder="hacker news username"
    >
      {userInfo && (
        <div className="stat-grid" style={{ marginBottom: 16 }}>
          <div className="stat-box">
            <div className="stat-val">{userInfo.karma?.toLocaleString()}</div>
            <div className="stat-label">Karma</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.submitted_count}</div>
            <div className="stat-label">Total Submissions</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{timeAgo(userInfo.created_utc)}</div>
            <div className="stat-label">Joined</div>
          </div>
        </div>
      )}
      {userInfo?.about && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-title">About</div>
          <p className="source-text">{userInfo.about}</p>
        </div>
      )}
      {submissions?.submissions?.length > 0 && (
        <>
          <div className="panel-title" style={{ marginBottom: 10 }}>RECENT SUBMISSIONS ({submissions.count})</div>
          <div className="card-grid">
            {submissions.submissions.map((s, i) => (
              <div className="source-card" key={i}>
                <div className="source-card-name">
                  <a href={s.url} target="_blank" rel="noreferrer">{s.title}</a>
                </div>
                <div className="source-card-meta">
                  <span><Heart size={11} /> {s.score}</span>
                  <span><MessageCircle size={11} /> {s.descendants}</span>
                  <span><Clock size={11} /> {timeAgo(s.time)}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </SourceTabShell>
  )
}

// ── X / Twitter ─────────────────────────────────────────
function XTab() {
  const [username, setUsername] = useState('')
  const [userInfo, setUserInfo] = useState(null)
  const [tweets, setTweets] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load() {
    if (!username.trim()) return
    setLoading(true); setError(null); setUserInfo(null); setTweets(null)
    try {
      const [u, t] = await Promise.all([
        sources.x.user(username),
        sources.x.tweets(username),
      ])
      setUserInfo(u); setTweets(t)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const hasTokenError = userInfo?.error

  return (
    <SourceTabShell
      username={username} setUsername={setUsername}
      onSearch={load} loading={loading} error={error}
      placeholder="X / Twitter username"
    >
      {hasTokenError && (
        <div className="error-box" style={{ marginBottom: 12 }}>{userInfo.error}</div>
      )}
      {userInfo && !hasTokenError && (
        <div className="stat-grid" style={{ marginBottom: 16 }}>
          <div className="stat-box">
            <div className="stat-val">{userInfo.display_name || userInfo.username}</div>
            <div className="stat-label">Display Name</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.followers_count?.toLocaleString()}</div>
            <div className="stat-label">Followers</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.following_count?.toLocaleString()}</div>
            <div className="stat-label">Following</div>
          </div>
          <div className="stat-box">
            <div className="stat-val">{userInfo.tweet_count?.toLocaleString()}</div>
            <div className="stat-label">Tweets</div>
          </div>
        </div>
      )}
      {userInfo?.description && !hasTokenError && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-title">Bio</div>
          <p className="source-text">{userInfo.description}</p>
        </div>
      )}
      {tweets?.tweets?.length > 0 && !hasTokenError && (
        <>
          <div className="panel-title" style={{ marginBottom: 10 }}>RECENT TWEETS ({tweets.count})</div>
          <div className="card-grid">
            {tweets.tweets.map((t, i) => (
              <div className="source-card" key={i}>
                <div className="source-card-desc">{t.text}</div>
                <div className="source-card-meta">
                  <span><Heart size={11} /> {t.likes}</span>
                  <span><MessageCircle size={11} /> {t.replies}</span>
                  <span><Clock size={11} /> {timeAgo(t.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </SourceTabShell>
  )
}

// ── Dev.to ──────────────────────────────────────────────
function DevtoTab() {
  const [username, setUsername] = useState('')
  const [userInfo, setUserInfo] = useState(null)
  const [articles, setArticles] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load() {
    if (!username.trim()) return
    setLoading(true); setError(null); setUserInfo(null); setArticles(null)
    try {
      const [u, a] = await Promise.all([
        sources.devto.user(username),
        sources.devto.articles(username),
      ])
      setUserInfo(u); setArticles(a)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell
      username={username} setUsername={setUsername}
      onSearch={load} loading={loading} error={error}
      placeholder="dev.to username"
    >
      {userInfo && (
        <div className="stat-grid" style={{ marginBottom: 16 }}>
          {userInfo.name && (
            <div className="stat-box">
              <div className="stat-val" style={{ fontSize: 16 }}>{userInfo.name}</div>
              <div className="stat-label">Name</div>
            </div>
          )}
          {userInfo.location && (
            <div className="stat-box">
              <div className="stat-val" style={{ fontSize: 14 }}>{userInfo.location}</div>
              <div className="stat-label">Location</div>
            </div>
          )}
          {userInfo.github_username && (
            <div className="stat-box">
              <div className="stat-val" style={{ fontSize: 14 }}>{userInfo.github_username}</div>
              <div className="stat-label">GitHub</div>
            </div>
          )}
          {userInfo.website_url && (
            <div className="stat-box">
              <div className="stat-val" style={{ fontSize: 12, wordBreak: 'break-all' }}>{userInfo.website_url}</div>
              <div className="stat-label">Website</div>
            </div>
          )}
        </div>
      )}
      {userInfo?.bio && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-title">Bio</div>
          <p className="source-text">{userInfo.bio}</p>
        </div>
      )}
      {articles?.articles?.length > 0 && (
        <>
          <div className="panel-title" style={{ marginBottom: 10 }}>ARTICLES ({articles.count})</div>
          <div className="card-grid">
            {articles.articles.map((a, i) => (
              <div className="source-card" key={i}>
                <div className="source-card-name">
                  <a href={a.url} target="_blank" rel="noreferrer">{a.title}</a>
                </div>
                <div className="source-card-desc">{a.description || <span className="muted-italic">No description</span>}</div>
                <div className="source-card-meta">
                  <span><Heart size={11} /> {a.positive_reactions}</span>
                  <span><MessageCircle size={11} /> {a.comments_count}</span>
                  <span><BookOpen size={11} /> {a.reading_time_minutes} min</span>
                  <span><Clock size={11} /> {timeAgo(a.published_at)}</span>
                  {a.tags?.slice(0, 3).map((t, j) => <span className="tag tag-blue" key={j}>{t}</span>)}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </SourceTabShell>
  )
}

// ── Shared wrapper for each tab ─────────────────────────
function SourceTabShell({ username, setUsername, onSearch, loading, error, placeholder, children }) {
  return (
    <>
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">Username</label>
            <input
              className="form-input"
              placeholder={placeholder}
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && onSearch()}
            />
          </div>
          <button className="btn btn-primary" onClick={onSearch} disabled={loading}>
            <Search size={13} /> {loading ? 'Fetching...' : 'Lookup'}
          </button>
        </div>
      </div>
      {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}
      {children}
      {!loading && !error && !children && (
        <div className="empty-state">
          <Search size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
          <div>Enter a username above to look up on this source</div>
        </div>
      )}
      {loading && <div className="loading"><div className="spinner" /> Fetching data...</div>}
    </>
  )
}

// ── Page root ──────────────────────────────────────────
export default function SourcesPage() {
  const [tab, setTab] = useState('gitlab')

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">MULTI-SOURCE INTELLIGENCE</div>
        <div className="page-sub">Cross-platform user reconnaissance — GitLab, Reddit, HN, X, Dev.to</div>
      </div>

      <div className="tabs">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`tab ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'gitlab'     && <GitLabTab />}
      {tab === 'reddit'     && <RedditTab />}
      {tab === 'hackernews' && <HackerNewsTab />}
      {tab === 'x'          && <XTab />}
      {tab === 'devto'      && <DevtoTab />}
    </div>
  )
}
