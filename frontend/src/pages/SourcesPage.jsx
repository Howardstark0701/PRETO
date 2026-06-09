import { useState } from 'react'
import { Search, ExternalLink, MessageCircle, Heart, BookOpen, Clock, Star, GitFork } from 'lucide-react'
import { sources } from '../api'

const TABS = [
  { id: 'gitlab',     label: 'GITLAB',     cls: 'source-badge-gitlab' },
  { id: 'reddit',     label: 'REDDIT',     cls: 'source-badge-reddit' },
  { id: 'hackernews', label: 'HACKERNEWS', cls: 'source-badge-hn'     },
  { id: 'x',          label: 'X',          cls: 'source-badge-x'      },
  { id: 'devto',      label: 'DEV.TO',     cls: 'source-badge-devto'  },
]

function timeAgo(ts) {
  if (!ts) return ''
  const now = Date.now() / 1000
  const s = typeof ts === 'number' ? ts : new Date(ts).getTime() / 1000
  const d = now - s
  if (d < 60) return 'NOW'
  if (d < 3600) return `${Math.floor(d / 60)}M AGO`
  if (d < 86400) return `${Math.floor(d / 3600)}H AGO`
  return `${Math.floor(d / 86400)}D AGO`
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
    <SourceTabShell username={username} setUsername={setUsername} onSearch={load} loading={loading} error={error} placeholder="e.g. torvalds" hint="Enter the GitLab username (no @ or prefix)" sourceCls="source-badge-gitlab">
      {projects?.projects?.length > 0 && (
        <>
          <div className="panel-header" style={{ marginBottom: 10 }}>PROJECTS ({projects.count})</div>
          <div className="card-grid">
            {projects.projects.map((p, i) => (
              <SourceCard key={i} name={p.full_name || p.name} desc={p.description} url={p.url}
                meta={<><span><Star size={10} /> {p.stargazers_count}</span><span><GitFork size={10} /> {p.forks_count}</span></>}
                tags={[p.language, ...(p.topics?.slice(0, 2) || [])].filter(Boolean)} sourceCls="source-badge-gitlab" />
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
      const [u, p] = await Promise.all([sources.reddit.user(username), sources.reddit.submissions(username)])
      setUserInfo(u); setPosts(p)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell username={username} setUsername={setUsername} onSearch={load} loading={loading} error={error} placeholder="e.g. spez" hint="Enter username only — no u/ or r/ prefix" sourceCls="source-badge-reddit">
      {userInfo && (
        <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 16 }}>
          <StatBox val={userInfo.link_karma?.toLocaleString()} label="LINK KARMA" />
          <StatBox val={userInfo.comment_karma?.toLocaleString()} label="COMMENT KARMA" />
          <StatBox val={userInfo.subreddit || '—'} label="PRIMARY SUB" />
          <StatBox val={userInfo.is_gold ? 'YES' : 'NO'} label="GOLD" />
        </div>
      )}
      {posts?.posts?.length > 0 && (
        <>
          <div className="panel-header" style={{ marginBottom: 10 }}>RECENT POSTS ({posts.count})</div>
          <div className="card-grid">
            {posts.posts.map((p, i) => (
              <SourceCard key={i} name={p.title} url={p.permalink}
                desc={<span className="status-badge status-critical" style={{ fontSize: 8 }}>{p.subreddit}</span>}
                meta={<><span><Heart size={10} /> {p.score}</span><span><MessageCircle size={10} /> {p.num_comments}</span><span><Clock size={10} /> {timeAgo(p.created_utc)}</span></>}
                sourceCls="source-badge-reddit" />
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
      const [u, s] = await Promise.all([sources.hackernews.user(username), sources.hackernews.submissions(username)])
      setUserInfo(u); setSubmissions(s)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell username={username} setUsername={setUsername} onSearch={load} loading={loading} error={error} placeholder="e.g. dang" hint="Enter HN username exactly as shown on the profile" sourceCls="source-badge-hn">
      {userInfo && (
        <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 16 }}>
          <StatBox val={userInfo.karma?.toLocaleString()} label="KARMA" />
          <StatBox val={userInfo.submitted_count} label="SUBMISSIONS" />
          <StatBox val={timeAgo(userInfo.created_utc)} label="JOINED" />
        </div>
      )}
      {userInfo?.about && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-header">ABOUT</div>
          <div style={{ fontFamily: 'var(--font-ui)', fontSize: 11, color: 'var(--text-dim)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{userInfo.about}</div>
        </div>
      )}
      {submissions?.submissions?.length > 0 && (
        <>
          <div className="panel-header" style={{ marginBottom: 10 }}>SUBMISSIONS ({submissions.count})</div>
          <div className="card-grid">
            {submissions.submissions.map((s, i) => (
              <SourceCard key={i} name={s.title} url={s.url}
                meta={<><span><Heart size={10} /> {s.score}</span><span><MessageCircle size={10} /> {s.descendants}</span><span><Clock size={10} /> {timeAgo(s.time)}</span></>}
                sourceCls="source-badge-hn" />
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
      const [u, t] = await Promise.all([sources.x.user(username), sources.x.tweets(username)])
      setUserInfo(u); setTweets(t)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const hasTokenError = userInfo?.error

  return (
    <SourceTabShell username={username} setUsername={setUsername} onSearch={load} loading={loading} error={error} placeholder="e.g. elonmusk" hint="Enter username without @ symbol" sourceCls="source-badge-x">
      {hasTokenError && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{userInfo.error}</div>}
      {userInfo && !hasTokenError && (
        <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 16 }}>
          <StatBox val={userInfo.display_name || userInfo.username} label="DISPLAY NAME" />
          <StatBox val={userInfo.followers_count?.toLocaleString()} label="FOLLOWERS" />
          <StatBox val={userInfo.following_count?.toLocaleString()} label="FOLLOWING" />
          <StatBox val={userInfo.tweet_count?.toLocaleString()} label="TWEETS" />
        </div>
      )}
      {userInfo?.description && !hasTokenError && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-header">BIO</div>
          <div style={{ fontFamily: 'var(--font-ui)', fontSize: 11, color: 'var(--text-dim)' }}>{userInfo.description}</div>
        </div>
      )}
      {tweets?.tweets?.length > 0 && !hasTokenError && (
        <>
          <div className="panel-header" style={{ marginBottom: 10 }}>RECENT TWEETS ({tweets.count})</div>
          <div className="card-grid">
            {tweets.tweets.map((t, i) => (
              <SourceCard key={i} name={t.text} desc={<span className="status-badge status-stable" style={{ fontSize: 8 }}>X</span>}
                meta={<><span><Heart size={10} /> {t.likes}</span><span><MessageCircle size={10} /> {t.replies}</span><span><Clock size={10} /> {timeAgo(t.created_at)}</span></>}
                sourceCls="source-badge-x" />
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
      const [u, a] = await Promise.all([sources.devto.user(username), sources.devto.articles(username)])
      setUserInfo(u); setArticles(a)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  return (
    <SourceTabShell username={username} setUsername={setUsername} onSearch={load} loading={loading} error={error} placeholder="e.g. ben" hint="Enter the Dev.to username from their profile URL" sourceCls="source-badge-devto">
      {userInfo && (
        <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 16 }}>
          {userInfo.name && <StatBox val={userInfo.name} label="NAME" />}
          {userInfo.location && <StatBox val={userInfo.location} label="LOCATION" />}
          {userInfo.github_username && <StatBox val={userInfo.github_username} label="GITHUB" />}
          {userInfo.website_url && <StatBox val={userInfo.website_url} label="WEBSITE" />}
        </div>
      )}
      {userInfo?.bio && (
        <div className="panel" style={{ marginBottom: 16 }}>
          <div className="panel-header">BIO</div>
          <div style={{ fontFamily: 'var(--font-ui)', fontSize: 11, color: 'var(--text-dim)' }}>{userInfo.bio}</div>
        </div>
      )}
      {articles?.articles?.length > 0 && (
        <>
          <div className="panel-header" style={{ marginBottom: 10 }}>ARTICLES ({articles.count})</div>
          <div className="card-grid">
            {articles.articles.map((a, i) => (
              <SourceCard key={i} name={a.title} desc={a.description} url={a.url}
                meta={<><span><Heart size={10} /> {a.positive_reactions}</span><span><MessageCircle size={10} /> {a.comments_count}</span><span><BookOpen size={10} /> {a.reading_time_minutes}MIN</span><span><Clock size={10} /> {timeAgo(a.published_at)}</span></>}
                tags={a.tags?.slice(0, 3)} sourceCls="source-badge-devto" />
            ))}
          </div>
        </>
      )}
    </SourceTabShell>
  )
}

// ── Shared widgets ─────────────────────────────────────
function StatBox({ val, label }) {
  return (
    <div className="stat-box">
      <div className="stat-val" style={{ fontSize: 16 }}>{val ?? '—'}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

function SourceCard({ name, desc, meta, tags, url, sourceCls }) {
  return (
    <div className="repo-card" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: 6 }}>
        <span className={`status-badge ${sourceCls}`} style={{ fontSize: 8, marginBottom: 6 }}>● {sourceCls.replace('source-badge-', '').toUpperCase()}</span>
        <div className="repo-card-name" style={{ fontSize: 12 }}>
          {url ? <a href={url} target="_blank" rel="noreferrer">{name}</a> : name}
        </div>
        <div className="repo-card-desc">{typeof desc === 'string' ? (desc || <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>NO DESCRIPTION</span>) : desc}</div>
      </div>
      {tags?.length > 0 && (
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 6 }}>
          {tags.map((t, i) => t && <span key={i} className="status-badge status-info" style={{ fontSize: 8, padding: '1px 5px' }}>{t}</span>)}
        </div>
      )}
      <div className="repo-card-meta" style={{ marginTop: 'auto' }}>{meta}</div>
    </div>
  )
}

function SourceTabShell({ username, setUsername, onSearch, loading, error, placeholder, hint, sourceCls, children }) {
  return (
    <>
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">USERNAME</label>
            <input className="form-input" style={{ fontFamily: 'var(--font-mono)', fontSize: 11 }}
              placeholder={placeholder} value={username}
              onChange={e => setUsername(e.target.value)} onKeyDown={e => e.key === 'Enter' && onSearch()} />
            {hint && (
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-muted)', marginTop: 4, letterSpacing: 0.5 }}>
                ⓘ {hint}
              </div>
            )}
          </div>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={onSearch} disabled={loading}>
            <Search size={12} /> QUERY SOURCE
          </button>
          <span className={`status-badge ${sourceCls}`} style={{ marginTop: 16, alignSelf: 'flex-end' }}>● {sourceCls.replace('source-badge-', '').toUpperCase()}</span>
        </div>
      </div>
      {error && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{error}</div>}
      {children}
      {!loading && !error && !children && (
        <div className="empty-state">
          <Search size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
          <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1 }}>ENTER USERNAME TO QUERY SOURCE</div>
        </div>
      )}
      {loading && (
        <div className="empty-state">
          <div className="skeleton skeleton-line" style={{ width: '50%', margin: '0 auto' }} />
          <div className="skeleton skeleton-line" style={{ width: '30%', margin: '8px auto 0' }} />
        </div>
      )}
    </>
  )
}

// ── Page root ──────────────────────────────────────────
export default function SourcesPage() {
  const [tab, setTab] = useState('gitlab')

  return (
    <div className="page">
      <div className="breadcrumb">OSINT COMMAND / MULTI_SOURCE_INTEL</div>

      <div className="mode-b-tabs">
        {TABS.map(t => (
          <button key={t.id} className={`mode-b-tab ${tab === t.id ? 'active' : ''}`}
            style={tab === t.id ? { color: 'var(--accent)', borderBottomColor: 'var(--accent)' } : {}}
            onClick={() => setTab(t.id)}>
            ● {t.label}
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
