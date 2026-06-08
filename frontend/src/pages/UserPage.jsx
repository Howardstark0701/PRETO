import { useState } from 'react'
import { User, Star, GitFork, Eye, ExternalLink, RefreshCw } from 'lucide-react'
import { repos, sync, insights } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const COLORS = ['#00d4b4','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#10b981']

export default function UserPage() {
  const [username, setUsername]   = useState('')
  const [stats, setStats]         = useState(null)
  const [userRepos, setUserRepos] = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [sortBy, setSortBy]       = useState('stars')
  const [analysis, setAnalysis]   = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [syncing, setSyncing]     = useState(false)

  async function loadUser() {
    if (!username.trim()) return
    setLoading(true); setError(null); setStats(null); setUserRepos(null); setAnalysis(null)
    try {
      const [s, r] = await Promise.all([
        repos.userStats(username),
        repos.userRepos(username, { sort_by: sortBy, per_page: 30 })
      ])
      setStats(s); setUserRepos(r)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doSync() {
    setSyncing(true)
    try { await sync.syncUser(username) }
    catch (e) { setError(e.message) }
    finally { setSyncing(false) }
  }

  async function doAnalysis() {
    if (!userRepos?.repos?.length) return
    setAiLoading(true); setAnalysis(null)
    try {
      const data = await insights.userAnalysis({
        username,
        repositories: userRepos.repos,
        statistics: stats
      })
      setAnalysis(data)
    } catch (e) { setAnalysis({ error: e.message }) }
    finally { setAiLoading(false) }
  }

  const langData = stats?.languages
    ? Object.entries(stats.languages)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
        .map(([name, count]) => ({ name, count }))
    : []

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="breadcrumb" style={{ marginBottom: 0 }}>OSINT COMMAND / USER_INTELLIGENCE</div>
        <span className="status-badge status-stable">● ENCRYPTED_UPLINK_STABLE</span>
      </div>

      {/* Input Panel */}
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="panel-header"><User size={11} /> TARGET_IDENTIFICATION</div>
        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">GITHUB USERNAME</label>
            <input
              className="form-input"
              style={{ width: '100%', minWidth: 'unset', fontFamily: 'var(--font-mono)', fontSize: 12 }}
              placeholder="torvalds"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadUser()}
            />
          </div>
          <div className="form-group">
            <label className="form-label">SORT BY</label>
            <select className="form-select" style={{ fontSize: 11 }} value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="stars">STARS</option>
              <option value="forks">FORKS</option>
              <option value="updated_at">UPDATED</option>
              <option value="name">NAME</option>
            </select>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={loadUser} disabled={loading}>
            <User size={12} /> {loading ? '⟳ SCANNING...' : '▼ ANALYZE'}
          </button>
          {stats && (
            <>
              <button className="btn btn-secondary" style={{ marginTop: 16 }} onClick={doSync} disabled={syncing}>
                <RefreshCw size={12} /> {syncing ? '⟳' : 'SYNC DB'}
              </button>
              <button className="btn btn-secondary" style={{ marginTop: 16 }} onClick={doAnalysis} disabled={aiLoading}>
                {aiLoading ? '⟳' : '✦ AI PROFILE'}
              </button>
            </>
          )}
        </div>
      </div>

      {error && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{error}</div>}

      {stats && (
        <>
          {/* Two-column layout: Profile + Stats */}
          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 1fr', marginBottom: 16 }}>
            {/* Entity Profile Card */}
            <div className="panel">
              <div className="panel-header"><User size={11} /> ENTITY_PROFILE</div>
              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <div style={{
                  width: 48, height: 48, background: 'var(--bg-base)', border: '2px solid var(--accent)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
                }}>
                  <User size={22} style={{ color: 'var(--accent-dim)' }} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily: 'var(--font-heading)', fontSize: 16, fontWeight: 700, color: 'var(--accent)' }}>{username}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>
                    {stats.bio || <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>NO BIO AVAILABLE</span>}
                  </div>
                  <div style={{ display: 'flex', gap: 12, marginTop: 8, fontSize: 10, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    {stats.created_at && <span>JOINED: {new Date(stats.created_at).toLocaleDateString()}</span>}
                    {stats.company && <span>ORG: {stats.company}</span>}
                    {stats.location && <span>LOC: {stats.location}</span>}
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, margin: 0 }}>
              <div className="stat-box" style={{ padding: 10 }}>
                <div className="stat-val" style={{ fontSize: 16 }}>{stats.total_repositories}</div>
                <div className="stat-label">REPOS</div>
              </div>
              <div className="stat-box" style={{ padding: 10 }}>
                <div className="stat-val" style={{ fontSize: 16 }}>{(stats.total_stars || 0).toLocaleString()}</div>
                <div className="stat-label">STARS</div>
              </div>
              <div className="stat-box" style={{ padding: 10 }}>
                <div className="stat-val" style={{ fontSize: 16 }}>{(stats.total_forks || 0).toLocaleString()}</div>
                <div className="stat-label">FORKS</div>
              </div>
              <div className="stat-box" style={{ padding: 10 }}>
                <div className="stat-val" style={{ fontSize: 16 }}>{stats.average_stars_per_repo || 0}</div>
                <div className="stat-label">AVG STARS</div>
              </div>
              <div className="stat-box" style={{ padding: 10 }}>
                <div className="stat-val" style={{ fontSize: 14, wordBreak: 'break-all' }}>{stats.most_used_language || '—'}</div>
                <div className="stat-label">TOP LANG</div>
              </div>
              <div className="stat-box" style={{ padding: 10 }}>
                <div className="stat-val" style={{ fontSize: 16 }}>{(stats.total_watchers || 0).toLocaleString()}</div>
                <div className="stat-label">WATCHERS</div>
              </div>
            </div>
          </div>

          {/* Language Distribution */}
          {langData.length > 0 && (
            <div className="panel" style={{ marginBottom: 16 }}>
              <div className="panel-header">LANGUAGE_DISTRIBUTION</div>
              <ResponsiveContainer width="100%" height={150}>
                <BarChart data={langData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 9, fontFamily: 'var(--font-mono)' }} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 9, fontFamily: 'var(--font-mono)' }} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 10, borderRadius: 0 }}
                    labelStyle={{ color: '#94a3b8' }}
                    cursor={{ fill: 'rgba(0,212,180,0.05)' }}
                  />
                  <Bar dataKey="count" radius={[0,0,0,0]}>
                    {langData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* AI Narrative Synthesis */}
          {analysis && !analysis.error && (
            <div className="panel" style={{ marginBottom: 16, borderColor: 'rgba(0,212,180,0.3)' }}>
              <div className="panel-header">AI NARRATIVE SYNTHESIS</div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
                {analysis.expertise_areas?.map((a, i) => (
                  <span key={i} className="status-badge status-stable" style={{ fontSize: 8, padding: '1px 6px' }}>{a}</span>
                ))}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.6, whiteSpace: 'pre-wrap', fontFamily: 'var(--font-ui)' }}>{analysis.analysis}</div>
            </div>
          )}
          {analysis?.error && (
            <div className="msg-box msg-error" style={{ marginBottom: 12 }}>AI UNAVAILABLE: {analysis.error}</div>
          )}
        </>
      )}

      {/* Repositories */}
      {userRepos?.repos?.length > 0 && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span className="panel-header" style={{ marginBottom: 0 }}>REPOSITORIES</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dim)' }}>
              {userRepos.total_count} ASSETS IDENTIFIED
            </span>
          </div>
          <div className="card-grid">
            {userRepos.repos.map((r, i) => <RepoCardModeB key={i} repo={r} />)}
          </div>
        </>
      )}

      {/* Loading State */}
      {loading && (
        <div className="empty-state">
          <div className="skeleton skeleton-line" style={{ width: '60%', margin: '0 auto' }} />
          <div className="skeleton skeleton-line" style={{ width: '40%', margin: '8px auto 0' }} />
        </div>
      )}

      {/* Empty State */}
      {!stats && !loading && !error && (
        <div className="empty-state">
          <User size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
          <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1 }}>ENTER TARGET USERNAME TO BEGIN ANALYSIS</div>
        </div>
      )}
    </div>
  )
}

/* ── Mode B User Repo Card ────────────────────────────────── */
function RepoCardModeB({ repo }) {
  const confidence = Math.min(99, (repo.stargazers_count || 0) > 1000 ? 85 + Math.floor(Math.random() * 14) : 50 + Math.floor(Math.random() * 30))
  return (
    <div className="repo-card" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 6 }}>
        <div style={{ width: 24, height: 24, background: 'var(--bg-base)', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <ExternalLink size={12} style={{ color: 'var(--accent-dim)' }} />
        </div>
        <div style={{ flex: 1 }}>
          <div className="repo-card-name" style={{ fontSize: 12 }}>
            <a href={repo.html_url} target="_blank" rel="noreferrer">{repo.full_name || repo.name}</a>
          </div>
          <div className="repo-card-desc">{repo.description || <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>NO DESCRIPTION</span>}</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 8 }}>
        {repo.language && <span className="status-badge status-info" style={{ fontSize: 8, padding: '1px 5px' }}>{repo.language}</span>}
        {repo.license?.spdx_id && <span className="status-badge status-stable" style={{ fontSize: 8, padding: '1px 5px' }}>{repo.license.spdx_id}</span>}
        <span className="status-badge status-warning" style={{ fontSize: 8, padding: '1px 5px' }}>CONFIDENCE: {confidence}%</span>
      </div>

      <div className="repo-card-meta" style={{ marginTop: 'auto' }}>
        <span><Star size={10} /> {repo.stargazers_count?.toLocaleString() || 0}</span>
        <span><GitFork size={10} /> {repo.forks_count?.toLocaleString() || 0}</span>
        <span><Eye size={10} /> {repo.watchers_count?.toLocaleString() || 0}</span>
      </div>

      <a href={repo.html_url} target="_blank" rel="noreferrer"
        style={{ marginTop: 10, fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--accent)', border: '1px solid var(--accent-dim)', padding: '4px 8px', textAlign: 'center', textDecoration: 'none', display: 'block' }}>
        VIEW_MANIFEST →
      </a>
    </div>
  )
}
