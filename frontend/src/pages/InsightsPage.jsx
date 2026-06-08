import { useState, useEffect, useRef } from 'react'
import { Brain, MessageSquare, Activity, List, Clock, ExternalLink } from 'lucide-react'
import { insights, sources, repos } from '../api'

const DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"

const SOURCE_COLORS = { github: '#6e7681', reddit: '#ff4500', hackernews: '#ff6600', devto: '#7c3aed', gitlab: '#fc6d26', x: '#e7e9ea' }
const ALL_SOURCES = ['github','reddit','hn','devto','gitlab','x']

export default function InsightsPage() {
  const [tab, setTab]             = useState('query')
  const [health, setHealth]       = useState(null)
  const [models, setModels]       = useState([])
  const [model, setModel]         = useState(() => localStorage.getItem('preto-ai-model') || DEFAULT_MODEL)
  const [query, setQuery]         = useState('')
  const [answer, setAnswer]       = useState('')
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [analyzeJson, setAnalyzeJson] = useState('[]')
  const [analysisType, setAnalysisType] = useState('general')
  const [analysisResult, setAnalysisResult] = useState(null)

  // Activity feed state
  const [feedUsername, setFeedUsername] = useState('')
  const [feedEvents, setFeedEvents]     = useState([])
  const [feedLoading, setFeedLoading]   = useState(false)
  const [feedError, setFeedError]       = useState(null)
  const [feedView, setFeedView]         = useState('list')
  const [activeSources, setActiveSources] = useState(() => new Set(ALL_SOURCES))
  const activeSourcesRef = useRef(activeSources)
  activeSourcesRef.current = activeSources

  function toggleSource(s) {
    setActiveSources(prev => {
      const next = new Set(prev)
      if (next.has(s)) next.delete(s); else next.add(s)
      return next
    })
  }

  useEffect(() => {
    insights.health()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable' }))
    insights.models()
      .then(d => { setModels(d.models); if (!d.models.some(m => m.id === model)) setModel(d.default) })
      .catch(() => {})
  }, [])

  useEffect(() => { localStorage.setItem('preto-ai-model', model) }, [model])

  async function doQuery() {
    if (!query.trim()) return
    setLoading(true); setAnswer(''); setError(null)
    try {
      const data = await insights.query({ query, model })
      setAnswer(data.answer)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doAnalyze() {
    setLoading(true); setAnalysisResult(null); setError(null)
    try {
      const repoList = JSON.parse(analyzeJson)
      const data = await insights.analyze({ repositories: repoList, analysis_type: analysisType, model })
      setAnalysisResult(data)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function loadActivityFeed() {
    if (!feedUsername.trim()) return
    setFeedLoading(true); setFeedError(null); setFeedEvents([])
    const events = []

    const promises = {}
    const active = activeSourcesRef.current

    if (active.has('reddit'))
      promises.reddit = sources.reddit.submissions(feedUsername, 10).catch(() => ({ posts: [] }))
    if (active.has('hn'))
      promises.hn = sources.hackernews.submissions(feedUsername, 10).catch(() => ({ submissions: [] }))
    if (active.has('x'))
      promises.x = sources.x.tweets(feedUsername, 10).catch(() => ({ tweets: [] }))
    if (active.has('devto'))
      promises.devto = sources.devto.articles(feedUsername, 10).catch(() => ({ articles: [] }))
    if (active.has('gitlab'))
      promises.gitlab = sources.gitlab.userProjects(feedUsername, 10).catch(() => ({ projects: [] }))
    if (active.has('github'))
      promises.github = repos.userRepos(feedUsername).catch(() => ({ repos: [] }))

    try {
      const results = await Promise.allSettled(Object.entries(promises).map(([k, v]) => v.then(d => [k, d])))
      for (const r of results) {
        if (r.status !== 'fulfilled') continue
        const [key, data] = r.value
        if (key === 'reddit' && data?.posts) {
          data.posts.forEach(p => events.push({
            source: 'reddit', ts: p.created_utc || p.created, title: p.title, url: p.url, username: feedUsername,
            engagement: { upvotes: p.ups || 0, comments: p.num_comments || 0 },
            type: 'post',
          }))
        }
        if (key === 'hn' && data?.submissions) {
          data.submissions.forEach(s => events.push({
            source: 'hackernews', ts: s.time || s.created_at, title: s.title, url: s.url, username: feedUsername,
            engagement: { upvotes: s.score || 0, comments: s.descendants || 0 },
            type: 'submission',
          }))
        }
        if (key === 'x' && data?.tweets) {
          data.tweets.forEach(t => events.push({
            source: 'x', ts: t.created_at, title: t.text, url: t.url, username: feedUsername,
            engagement: { likes: t.favorite_count || 0, retweets: t.retweet_count || 0 },
            type: 'tweet',
          }))
        }
        if (key === 'devto' && data?.articles) {
          data.articles.forEach(a => events.push({
            source: 'devto', ts: a.published_at, title: a.title, url: a.url, username: feedUsername,
            engagement: { likes: a.public_reactions_count || 0, comments: a.comments_count || 0 },
            type: 'article',
          }))
        }
        if (key === 'gitlab' && data?.projects) {
          data.projects.forEach(p => events.push({
            source: 'gitlab', ts: p.last_activity_at || p.created_at, title: p.name || p.path, url: p.web_url, username: feedUsername,
            engagement: { stars: p.star_count || 0, forks: p.forks_count || 0 },
            type: 'project',
          }))
        }
        if (key === 'github' && data?.repos) {
          data.repos.forEach(r => events.push({
            source: 'github', ts: r.updated_at || r.pushed_at || r.created_at, title: r.name, url: r.html_url, username: feedUsername,
            engagement: { stars: r.stargazers_count || 0, forks: r.forks_count || 0 },
            type: 'repo',
          }))
        }
      }
      events.sort((a, b) => {
        const ta = a.ts ? new Date(a.ts).getTime() : 0
        const tb = b.ts ? new Date(b.ts).getTime() : 0
        return tb - ta
      })
      setFeedEvents(events)
      if (events.length === 0) setFeedError('No activity found for this user on selected platforms')
    } catch (e) { setFeedError(e.message) }
    finally { setFeedLoading(false) }
  }

  const nimOk = health?.nim_configured

  return (
    <div className="page">
      <div className="breadcrumb">OSINT COMMAND / AI_INSIGHTS</div>

      {/* NIM Status Bar */}
      <div className="panel" style={{ marginBottom: 12, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <span className={`status-badge ${health?.status === 'healthy' ? 'status-operational' : 'status-critical'}`}>
          ● {health?.status?.toUpperCase() || 'UNKNOWN'}
        </span>
        <span className="status-badge status-info" style={{ fontSize: 8 }}>
          ● NIM: {nimOk ? 'CONFIGURED' : 'FALLBACK'}
        </span>
        {health?.rate_limit && (
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-dim)' }}>
            SLOTS: {health.rate_limit.available_slots}/{health.rate_limit_per_minute}
          </span>
        )}
        {models.length > 0 && (
          <select className="form-select" style={{ width: 'auto', marginLeft: 'auto', fontSize: 10, padding: '4px 8px' }}
            value={model} onChange={e => setModel(e.target.value)}>
            {models.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
          </select>
        )}
        {!nimOk && <span className="status-badge status-warning" style={{ fontSize: 8 }}>SET NIM_API_KEY IN .ENV</span>}
      </div>

      {/* Tabs */}
      <div className="mode-b-tabs">
        {[['query','QUERY_ENGINE'],['analyze','REPO_ANALYZER'],['activity','ACTIVITY_FEED']].map(([k, l]) => (
          <button key={k} className={`mode-b-tab ${tab === k ? 'active' : ''}`} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>

      {error && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{error}</div>}

      {/* ── Query Tab ── */}
      {tab === 'query' && (
        <div className="panel">
          <div className="panel-header"><MessageSquare size={11} /> NATURAL_LANGUAGE_QUERY</div>
          <div className="form-row" style={{ marginBottom: 12 }}>
            <textarea
              className="form-input"
              style={{ minWidth: 'unset', flex: 1, height: 80, resize: 'vertical', fontFamily: 'var(--font-mono)', fontSize: 12, background: 'var(--bg-terminal)' }}
              placeholder="SELECT * FROM osint_data WHERE query = 'most popular Python OSINT tools'..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={doQuery} disabled={loading || !query.trim()}>
            <MessageSquare size={12} /> {loading ? '⟳ QUERYING NIM...' : '▼ EXECUTE_QUERY'}
          </button>

          {answer && (
            <div style={{ marginTop: 16 }}>
              <div className="panel-header">NIM_RESPONSE</div>
              <div className="terminal-block" style={{ maxHeight: 400, background: 'var(--bg-terminal)' }}>
                <div className="terminal-line">{answer}</div>
              </div>
            </div>
          )}

          {loading && (
            <div style={{ marginTop: 16 }}>
              <div className="skeleton skeleton-title" />
              <div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '70%' }} />
            </div>
          )}

          {!answer && !loading && !error && (
            <div className="empty-state" style={{ marginTop: 8 }}>
              <Brain size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
              <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1, fontSize: 11 }}>AWAITING OPERATOR QUERY</div>
              <div style={{ fontSize: 10, marginTop: 6, color: 'var(--text-muted)' }}>Ask anything about your OSINT data</div>
            </div>
          )}
        </div>
      )}

      {/* ── Analyze Tab ── */}
      {tab === 'analyze' && (
        <div className="panel">
          <div className="panel-header"><Brain size={11} /> REPOSITORY_ANALYSIS_ENGINE</div>

          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 1fr', marginBottom: 12 }}>
            <div className="form-group">
              <label className="form-label">ANALYSIS TYPE</label>
              <select className="form-select" style={{ fontSize: 11 }} value={analysisType} onChange={e => setAnalysisType(e.target.value)}>
                <option value="general">GENERAL</option>
                <option value="security">SECURITY</option>
                <option value="trends">TRENDS</option>
                <option value="contributors">CONTRIBUTORS</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">MODEL</label>
              <select className="form-select" style={{ fontSize: 11 }} value={model} onChange={e => setModel(e.target.value)}>
                {models.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
              </select>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: 12 }}>
            <label className="form-label">REPOSITORIES (JSON ARRAY)</label>
            <textarea
              className="form-input"
              style={{ minWidth: 'unset', width: '100%', height: 100, resize: 'vertical', background: 'var(--bg-terminal)', fontFamily: 'var(--font-mono)', fontSize: 11 }}
              value={analyzeJson}
              onChange={e => setAnalyzeJson(e.target.value)}
              placeholder='[{"name": "repo", "stargazers_count": 100}]'
            />
          </div>
          <button className="btn btn-primary" onClick={doAnalyze} disabled={loading}>
            <Brain size={12} /> {loading ? '⟳ PROCESSING...' : '▼ RUN_ANALYSIS'}
          </button>

          {analysisResult && (
            <div style={{ marginTop: 16 }}>
              <div className="panel-header">ANALYSIS_OUTPUT</div>
              <div className="terminal-block" style={{ maxHeight: 300 }}>{JSON.stringify(analysisResult, null, 2)}</div>
            </div>
          )}

          {loading && (
            <div style={{ marginTop: 16 }}>
              <div className="skeleton skeleton-title" />
              <div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '60%' }} />
            </div>
          )}

          {!analysisResult && !loading && !error && (
            <div className="empty-state" style={{ marginTop: 8 }}>
              <Brain size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
              <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1, fontSize: 11 }}>REPOSITORY DATA AWAITING ANALYSIS</div>
            </div>
          )}
        </div>
      )}

      {/* ── Activity Feed Tab ── */}
      {tab === 'activity' && (
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div className="panel-header"><Activity size={11} /> CROSS_SOURCE_ACTIVITY_FEED</div>

          {/* Username input — full width */}
          <input className="form-input"
            style={{ width: '100%', minWidth: 'unset', fontFamily: 'var(--font-mono)', fontSize: 13, background: 'var(--bg-terminal)', border: '1px solid var(--accent)', letterSpacing: 0.5 }}
            placeholder="TARGET_USERNAME"
            value={feedUsername}
            onChange={e => setFeedUsername(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && loadActivityFeed()}
          />

          {/* Source filter pills + toggle group row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
            {/* Left side: FETCH button + platform pills */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
              <button className="btn btn-primary" onClick={loadActivityFeed} disabled={feedLoading} style={{ padding: '4px 14px', fontSize: 10, letterSpacing: 1 }}>
                {feedLoading ? '⟳ FETCHING...' : '▼ FETCH'}
              </button>
              {ALL_SOURCES.map(s => {
                const active = activeSources.has(s)
                const col = SOURCE_COLORS[s] || 'var(--text-muted)'
                return (
                  <button key={s} onClick={() => toggleSource(s)}
                    style={{
                      fontFamily: 'var(--font-mono)', fontSize: 9, letterSpacing: 1, cursor: 'pointer',
                      padding: '3px 10px', border: `1px solid ${active ? col : 'var(--border)'}`, background: active ? `${col}18` : 'transparent',
                      color: active ? col : 'var(--text-muted)', textTransform: 'uppercase',
                    }}>
                    {s === 'hn' ? 'HN' : s === 'x' ? 'X' : s.toUpperCase()}
                  </button>
                )
              })}
            </div>

            {/* Right side: view toggle group — shared inset container */}
            <div className="toggle-group">
              {['list','timeline'].map(v => (
                <button key={v} onClick={() => setFeedView(v)} className={feedView === v ? 'active' : ''}>
                  {v === 'list' ? <><List size={10} style={{ marginRight: 4, verticalAlign: 'middle' }} /> LIST</> : <><Clock size={10} style={{ marginRight: 4, verticalAlign: 'middle' }} /> TIMELINE</>}
                </button>
              ))}
            </div>
          </div>

          {/* Event count */}
          {feedEvents.length > 0 && !feedLoading && (
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-dim)', letterSpacing: 1, textAlign: 'right' }}>
              {feedEvents.length} EVENT{feedEvents.length !== 1 ? 'S' : ''} CAPTURED
            </div>
          )}

          {feedError && <div className="msg-box msg-error" style={{ marginBottom: 4, fontSize: 10 }}>{feedError}</div>}

          {/* Loading */}
          {feedLoading && (
            <div style={{ padding: 16 }}>
              {[1,2,3,4,5].map(i => <div key={i} className="skeleton skeleton-line" style={{ width: `${85 - i*10}%`, marginBottom: 6 }} />)}
            </div>
          )}

          {/* Empty state */}
          {!feedLoading && feedEvents.length === 0 && !feedError && (
            <div className="empty-state" style={{ marginTop: 4 }}>
              <Activity size={32} style={{ marginBottom: 6, opacity: 0.3 }} />
              <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1, fontSize: 11 }}>ENTER USERNAME TO SCAN ALL PLATFORMS</div>
              <div style={{ fontSize: 10, marginTop: 2, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>GITHUB · REDDIT · HN · DEV.TO · GITLAB · X</div>
            </div>
          )}

          {/* ── LIST VIEW ── */}
          {!feedLoading && feedEvents.length > 0 && feedView === 'list' && (() => {
            const grouped = {}
            const now = new Date()
            const todayStr = now.toISOString().slice(0,10)
            const yesterday = new Date(now); yesterday.setDate(yesterday.getDate() - 1)
            const yesterdayStr = yesterday.toISOString().slice(0,10)
            feedEvents.forEach(ev => {
              const d = ev.ts ? new Date(ev.ts).toISOString().slice(0,10) : 'unknown'
              if (!grouped[d]) grouped[d] = { label: d === todayStr ? `TODAY — ${d}` : d === yesterdayStr ? `YESTERDAY — ${d}` : d, events: [] }
              grouped[d].events.push(ev)
            })
            const sortedDates = Object.keys(grouped).sort((a,b) => b.localeCompare(a))

            return (
              <div style={{ display: 'flex', flexDirection: 'column', maxHeight: 520, overflowY: 'auto', scrollbarWidth: 'thin', scrollbarColor: 'var(--accent-dim) transparent' }}>
                {sortedDates.map(dateKey => {
                  const grp = grouped[dateKey]
                  return (
                    <div key={dateKey} style={{ marginBottom: 8 }}>
                      <div style={{
                        fontFamily: 'var(--font-mono)', fontSize: 9, letterSpacing: 1.5, color: 'var(--text-muted)',
                        padding: '4px 0 6px 0', borderBottom: '1px solid var(--border)', marginBottom: 4,
                      }}>
                        {grp.label}
                      </div>
                      {grp.events.map((ev, i) => {
                        const col = SOURCE_COLORS[ev.source] || 'var(--accent)'
                        const label = ev.source === 'hackernews' ? 'HN' : ev.source.toUpperCase()
                        return (
                          <div key={`${dateKey}-${i}`} style={{
                            display: 'flex', alignItems: 'center', gap: 8, padding: '5px 8px', fontSize: 11,
                            background: 'transparent', cursor: 'default',
                          }}
                            onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                          >
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-muted)', whiteSpace: 'nowrap', minWidth: 80 }}>
                              {ev.ts ? new Date(ev.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--:--'}
                            </span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 4, whiteSpace: 'nowrap', minWidth: 60, fontWeight: 700, fontSize: 10, color: col }}>
                              <span style={{ width: 6, height: 6, borderRadius: '50%', background: col, display: 'inline-block', flexShrink: 0 }} />
                              {label}
                            </span>
                            <span style={{ flex: 1, color: 'var(--text-dim)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 10 }}>
                              <span style={{ color: 'var(--text-muted)' }}>{ev.username || feedUsername} </span>
                              {ev.type === 'post' && 'posted '}
                              {ev.type === 'submission' && 'submitted '}
                              {ev.type === 'tweet' && 'tweeted '}
                              {ev.type === 'article' && 'published '}
                              {ev.type === 'repo' && 'updated repo '}
                              {ev.type === 'project' && 'updated project '}
                              {ev.url
                                ? <a href={ev.url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: 10 }}>{ev.title}</a>
                                : <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9 }}>{ev.title}</span>
                              }
                            </span>
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-muted)', whiteSpace: 'nowrap', display: 'flex', gap: 8, alignItems: 'center', minWidth: 80, justifyContent: 'flex-end' }}>
                              {ev.engagement?.stars != null && <span style={{ display: 'flex', alignItems: 'center', gap: 2 }}>★{ev.engagement.stars}</span>}
                              {ev.engagement?.forks != null && <span style={{ display: 'flex', alignItems: 'center', gap: 2 }}>⑂{ev.engagement.forks}</span>}
                              {ev.engagement?.upvotes != null && <span style={{ display: 'flex', alignItems: 'center', gap: 2 }}>▲{ev.engagement.upvotes}</span>}
                              {ev.engagement?.likes != null && <span style={{ display: 'flex', alignItems: 'center', gap: 2 }}>♥{ev.engagement.likes}</span>}
                              {ev.engagement?.retweets != null && <span style={{ display: 'flex', alignItems: 'center', gap: 2 }}>↻{ev.engagement.retweets}</span>}
                              {ev.engagement?.comments != null && <span style={{ display: 'flex', alignItems: 'center', gap: 2 }}>💬{ev.engagement.comments}</span>}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  )
                })}
              </div>
            )
          })()}

          {/* ── TIMELINE VIEW ── */}
          {!feedLoading && feedEvents.length > 0 && feedView === 'timeline' && (() => {
            const grouped = {}
            const now = new Date()
            const todayStr = now.toISOString().slice(0,10)
            const yesterday = new Date(now); yesterday.setDate(yesterday.getDate() - 1)
            const yesterdayStr = yesterday.toISOString().slice(0,10)
            feedEvents.forEach(ev => {
              const d = ev.ts ? new Date(ev.ts).toISOString().slice(0,10) : 'unknown'
              if (!grouped[d]) grouped[d] = { label: d === todayStr ? `TODAY • ${d}` : d === yesterdayStr ? `YESTERDAY • ${d}` : d, events: [] }
              grouped[d].events.push(ev)
            })
            const sortedDates = Object.keys(grouped).sort((a,b) => b.localeCompare(a))

            return (
              <div style={{ maxHeight: 520, overflowY: 'auto', scrollbarWidth: 'thin', scrollbarColor: 'var(--accent-dim) transparent' }}>
                {sortedDates.map(dateKey => {
                  const grp = grouped[dateKey]
                  return (
                    <div key={dateKey} style={{ marginBottom: 16 }}>
                      <div style={{
                        fontFamily: 'var(--font-mono)', fontSize: 9, letterSpacing: 1.5, color: 'var(--text-muted)',
                        padding: '4px 0 10px 0', marginLeft: 28,
                      }}>
                        {grp.label}
                      </div>
                      {/* Timeline spine */}
                      <div style={{ position: 'relative', paddingLeft: 28 }}>
                        <div style={{
                          position: 'absolute', left: 9, top: 0, bottom: 0, width: 2,
                          background: 'linear-gradient(to bottom, var(--accent), rgba(0,212,180,0.08))',
                        }} />
                        {grp.events.map((ev, i) => {
                          const col = SOURCE_COLORS[ev.source] || 'var(--accent)'
                          const label = ev.source === 'hackernews' ? 'HN' : ev.source.toUpperCase()
                          return (
                            <div key={`${dateKey}-${i}`} style={{
                              position: 'relative', paddingBottom: 12, marginBottom: 8,
                              background: 'var(--bg-card)', border: '1px solid var(--border)',
                              padding: '10px 12px 10px 16px',
                            }}>
                              {/* Timeline dot */}
                              <div style={{
                                position: 'absolute', left: -21, top: 12, width: 10, height: 10, borderRadius: '50%',
                                background: col, border: '2px solid var(--bg-panel)', zIndex: 1,
                              }} />
                              {/* Platform badge top-left */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                                <span style={{
                                  fontFamily: 'var(--font-mono)', fontSize: 8, letterSpacing: 1, fontWeight: 700,
                                  color: col, background: `${col}15`, padding: '1px 6px', textTransform: 'uppercase',
                                }}>
                                  ● {label}
                                </span>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 8, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                                  {ev.ts ? new Date(ev.ts).toLocaleString() : '—'}
                                </span>
                              </div>
                              {/* Action text */}
                              <div style={{ fontSize: 11, color: 'var(--text-dim)', lineHeight: 1.4, marginBottom: 6 }}>
                                <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 10 }}>{ev.username || feedUsername} </span>
                                {ev.type === 'post' && 'posted '}
                                {ev.type === 'submission' && 'submitted '}
                                {ev.type === 'tweet' && 'tweeted '}
                                {ev.type === 'article' && 'published '}
                                {ev.type === 'repo' && 'updated repo '}
                                {ev.type === 'project' && 'updated project '}
                                {ev.url
                                  ? <a href={ev.url} target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: 10 }}>{ev.title}</a>
                                  : <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9 }}>{ev.title}</span>
                                }
                              </div>
                              {/* Engagement bottom-left */}
                              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 8, color: 'var(--text-muted)', display: 'flex', gap: 8 }}>
                                {ev.engagement?.stars != null && <span>★{ev.engagement.stars}</span>}
                                {ev.engagement?.forks != null && <span>⑂{ev.engagement.forks}</span>}
                                {ev.engagement?.upvotes != null && <span>▲{ev.engagement.upvotes}</span>}
                                {ev.engagement?.likes != null && <span>♥{ev.engagement.likes}</span>}
                                {ev.engagement?.retweets != null && <span>↻{ev.engagement.retweets}</span>}
                                {ev.engagement?.comments != null && <span>💬{ev.engagement.comments}</span>}
                                {(!ev.engagement || Object.values(ev.engagement).every(v => v === 0)) && <span>—</span>}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
              </div>
            )
          })()}
        </div>
      )}
    </div>
  )
}
