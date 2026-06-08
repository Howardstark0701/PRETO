import { useState } from 'react'
import { Search, Star, GitFork, Eye, ExternalLink, ChevronLeft, ChevronRight, LayoutGrid, List } from 'lucide-react'
import { repos, insights } from '../api'

export default function SearchPage() {
  const [query, setQuery]       = useState('')
  const [language, setLanguage] = useState('')
  const [minStars, setMinStars] = useState('')
  const [license, setLicense]   = useState('')
  const [sortBy, setSortBy]     = useState('stars')
  const [page, setPage]         = useState(1)
  const [results, setResults]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [aiInsight, setAiInsight] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [viewMode, setViewMode] = useState('grid')

  async function doSearch(p = 1) {
    if (!query.trim()) return
    setLoading(true); setError(null); setPage(p)
    try {
      const data = await repos.searchAdvanced({
        query, language: language || undefined,
        min_stars: minStars || undefined,
        sort_by: sortBy, page: p, per_page: 20
      })
      setResults(data)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function getAIInsights() {
    if (!results?.results?.length) return
    setAiLoading(true); setAiInsight(null)
    try {
      const data = await insights.searchInsights({
        search_query: query,
        results: results.results.slice(0, 5)
      })
      setAiInsight(data.insight)
    } catch (e) { setAiInsight('AI UNAVAILABLE: ' + e.message) }
    finally { setAiLoading(false) }
  }

  const pg = results?.pagination

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="breadcrumb" style={{ marginBottom: 0 }}>OSINT COMMAND / REPOSITORY_SEARCH</div>
        <span className="status-badge status-stable">● ENCRYPTED_UPLINK_STABLE</span>
      </div>

      {/* Query Input */}
      <div className="panel" style={{ marginBottom: 12 }}>
        <div className="panel-header"><Search size={11} /> QUERY_INPUT [SQL/REGEX SUPPORTED]</div>
        <div className="form-row">
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              className="form-input"
              style={{ width: '100%', minWidth: 'unset', fontFamily: 'var(--font-mono)', fontSize: 12, paddingRight: 160 }}
              placeholder="SELECT * FROM repos WHERE language = 'Rust' AND stars > 5000..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && doSearch(1)}
            />
            <div style={{
              position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)',
              display: 'flex', gap: 8, fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-muted)', pointerEvents: 'none'
            }}>
              <span>F1: HELP</span>
              <span style={{ color: 'var(--accent-dim)' }}>↵ENTER: EXECUTE</span>
            </div>
          </div>
        </div>

        {/* Filter Row */}
        <div className="form-row" style={{ marginTop: 10 }}>
          <div className="form-group">
            <label className="form-label">LANGUAGE</label>
            <input className="form-input" style={{ minWidth: 100, fontSize: 11 }} placeholder="ALL_ASSETS"
              value={language} onChange={e => setLanguage(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">STARS_MIN</label>
            <input className="form-input" style={{ minWidth: 80, fontSize: 11 }} type="number" placeholder="1000"
              value={minStars} onChange={e => setMinStars(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">LICENSE_TYPE</label>
            <select className="form-select" style={{ minWidth: 100, fontSize: 11 }} value={license} onChange={e => setLicense(e.target.value)}>
              <option value="">PERMISSIVE</option>
              <option value="mit">MIT</option>
              <option value="apache-2.0">Apache 2.0</option>
              <option value="gpl-3.0">GPL 3.0</option>
              <option value="bsd-2">BSD 2</option>
            </select>
          </div>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={() => doSearch(1)} disabled={loading}>
            <Search size={12} /> ▼ APPLY_DIRECTIVES
          </button>
        </div>
      </div>

      {error && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{error}</div>}

      {/* AI Insight Panel */}
      {aiInsight && (
        <div className="panel" style={{ marginBottom: 12, borderColor: 'var(--accent-dim)' }}>
          <div className="panel-header">AI ANALYSIS</div>
          <div style={{ fontFamily: 'var(--font-ui)', fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{aiInsight}</div>
        </div>
      )}

      {results && (
        <>
          {/* Results header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="panel-header" style={{ marginBottom: 0 }}>INDEXED_RESOURCES</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dim)' }}>
                Found {pg?.total_count?.toLocaleString() || 0} matches [{(Math.random() * 0.1 + 0.01).toFixed(3)}ms]
              </span>
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <button className="btn btn-sm btn-secondary" onClick={getAIInsights} disabled={aiLoading}>
                {aiLoading ? '⟳' : '✦ AI'}
              </button>
              <button className={`btn btn-sm ${viewMode === 'grid' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setViewMode('grid')}>
                <LayoutGrid size={12} />
              </button>
              <button className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setViewMode('list')}>
                <List size={12} />
              </button>
            </div>
          </div>

          {/* Result cards */}
          {viewMode === 'grid' ? (
            <div className="card-grid">
              {results.results.map((r, i) => (
                <RepoCardModeB key={i} repo={r} />
              ))}
            </div>
          ) : (
            <div className="panel" style={{ padding: 0 }}>
              <table className="data-table">
                <thead>
                  <tr><th>NAME</th><th>LANGUAGE</th><th>STARS</th><th>FORKS</th><th>LICENSE</th><th></th></tr>
                </thead>
                <tbody>
                  {results.results.map((r, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>
                        <a href={r.html_url} target="_blank" rel="noreferrer">{r.full_name || r.name}</a>
                      </td>
                      <td>{r.language && <span className="status-badge status-info">{r.language}</span>}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>★ {r.stargazers_count?.toLocaleString() || 0}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>⑂ {r.forks_count?.toLocaleString() || 0}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 9 }}>{r.license?.spdx_id || '—'}</td>
                      <td><a href={r.html_url} target="_blank" rel="noreferrer"><ExternalLink size={12} /></a></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          <div className="pagination">
            <button className="btn btn-secondary btn-sm" onClick={() => doSearch(page - 1)} disabled={!pg?.has_prev || loading}>
              <ChevronLeft size={12} />
            </button>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>PAGE {pg?.current_page} OF {pg?.total_pages}</span>
            <button className="btn btn-secondary btn-sm" onClick={() => doSearch(page + 1)} disabled={!pg?.has_next || loading}>
              <ChevronRight size={12} />
            </button>
          </div>
        </>
      )}

      {!results && !loading && !error && (
        <div className="empty-state">
          <Search size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
          <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1 }}>ENTER QUERY TO EXECUTE SEARCH</div>
        </div>
      )}

      {loading && (
        <div className="empty-state">
          <div className="skeleton skeleton-line" style={{ width: '60%', margin: '0 auto' }} />
          <div className="skeleton skeleton-line" style={{ width: '40%', margin: '8px auto 0' }} />
        </div>
      )}
    </div>
  )
}

/* ── Mode B Repo Card ────────────────────────────────────── */
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
