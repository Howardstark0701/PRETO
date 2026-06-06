import { useState } from 'react'
import { User, Star, GitFork, Code, RefreshCw } from 'lucide-react'
import { repos, sync, insights } from '../api'
import RepoCard from '../components/RepoCard'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const COLORS = ['#00d4b4','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#10b981']

export default function UserPage() {
  const [username, setUsername] = useState('')
  const [stats, setStats]       = useState(null)
  const [userRepos, setUserRepos] = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [sortBy, setSortBy]     = useState('stars')
  const [analysis, setAnalysis] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [syncing, setSyncing]   = useState(false)

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
      <div className="page-header">
        <div className="page-title">USER INTELLIGENCE</div>
        <div className="page-sub">Profile analysis and repository mapping</div>
      </div>

      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">GitHub Username</label>
            <input
              className="form-input"
              placeholder="torvalds"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadUser()}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Sort By</label>
            <select className="form-select" value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="stars">Stars</option>
              <option value="forks">Forks</option>
              <option value="updated_at">Updated</option>
              <option value="name">Name</option>
            </select>
          </div>
          <button className="btn btn-primary" onClick={loadUser} disabled={loading}>
            <User size={13} /> {loading ? 'Loading...' : 'Analyze'}
          </button>
          {stats && (
            <>
              <button className="btn btn-secondary" onClick={doSync} disabled={syncing}>
                <RefreshCw size={13} /> {syncing ? 'Syncing...' : 'Sync DB'}
              </button>
              <button className="btn btn-secondary" onClick={doAnalysis} disabled={aiLoading}>
                {aiLoading ? 'Analyzing...' : '✦ AI Profile'}
              </button>
            </>
          )}
        </div>
      </div>

      {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}

      {stats && (
        <>
          <div className="stat-grid" style={{ marginBottom: 16 }}>
            <div className="stat-box">
              <div className="stat-val">{stats.total_repositories}</div>
              <div className="stat-label">Repositories</div>
            </div>
            <div className="stat-box">
              <div className="stat-val">{(stats.total_stars || 0).toLocaleString()}</div>
              <div className="stat-label">Total Stars</div>
            </div>
            <div className="stat-box">
              <div className="stat-val">{(stats.total_forks || 0).toLocaleString()}</div>
              <div className="stat-label">Total Forks</div>
            </div>
            <div className="stat-box">
              <div className="stat-val">{stats.average_stars_per_repo || 0}</div>
              <div className="stat-label">Avg Stars/Repo</div>
            </div>
            <div className="stat-box">
              <div className="stat-val" style={{ fontSize: 14 }}>{stats.most_used_language || '—'}</div>
              <div className="stat-label">Top Language</div>
            </div>
          </div>

          {langData.length > 0 && (
            <div className="panel" style={{ marginBottom: 16 }}>
              <div className="panel-title">LANGUAGE DISTRIBUTION</div>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={langData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 11 }}
                    cursor={{ fill: 'rgba(0,212,180,0.05)' }}
                  />
                  <Bar dataKey="count" radius={[3,3,0,0]}>
                    {langData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {analysis && !analysis.error && (
            <div className="panel" style={{ marginBottom: 16, borderColor: 'rgba(0,212,180,0.3)' }}>
              <div className="panel-title">AI PROFILE ANALYSIS</div>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 10 }}>
                {analysis.expertise_areas?.map((a, i) => (
                  <span key={i} className="badge badge-green">{a}</span>
                ))}
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{analysis.analysis}</p>
            </div>
          )}
        </>
      )}

      {userRepos?.repos?.length > 0 && (
        <>
          <div className="panel-title" style={{ marginBottom: 10 }}>
            REPOSITORIES ({userRepos.total_count})
          </div>
          <div className="card-grid">
            {userRepos.repos.map((r, i) => <RepoCard key={i} repo={r} />)}
          </div>
        </>
      )}

      {loading && <div className="loading"><div className="spinner" /> Fetching user profile...</div>}
      {!stats && !loading && !error && (
        <div className="empty-state">
          <User size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
          <div>Enter a GitHub username to begin analysis</div>
        </div>
      )}
    </div>
  )
}
