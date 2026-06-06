import { useState } from 'react'
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import { repos, insights } from '../api'
import RepoCard from '../components/RepoCard'

export default function SearchPage() {
  const [query, setQuery]       = useState('')
  const [language, setLanguage] = useState('')
  const [minStars, setMinStars] = useState('')
  const [sortBy, setSortBy]     = useState('stars')
  const [page, setPage]         = useState(1)
  const [results, setResults]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [aiInsight, setAiInsight] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)

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
    } catch (e) { setAiInsight('AI insights unavailable: ' + e.message) }
    finally { setAiLoading(false) }
  }

  const pg = results?.pagination

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">REPOSITORY SEARCH</div>
        <div className="page-sub">Query GitHub's public repository index</div>
      </div>

      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="form-row">
          <div className="form-group" style={{ flex: 2 }}>
            <label className="form-label">Query</label>
            <input
              className="form-input"
              style={{ minWidth: 'unset', width: '100%' }}
              placeholder="e.g. osint python scraper"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && doSearch(1)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Language</label>
            <input className="form-input" style={{ minWidth: 120 }} placeholder="Python" value={language} onChange={e => setLanguage(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Min Stars</label>
            <input className="form-input" style={{ minWidth: 90 }} type="number" placeholder="100" value={minStars} onChange={e => setMinStars(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Sort By</label>
            <select className="form-select" value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="stars">Stars</option>
              <option value="forks">Forks</option>
              <option value="watchers">Watchers</option>
              <option value="updated_at">Updated</option>
              <option value="name">Name</option>
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => doSearch(1)} disabled={loading}>
            <Search size={13} /> {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}

      {results && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {pg?.total_count?.toLocaleString()} results · page {pg?.current_page}/{pg?.total_pages}
            </span>
            <button className="btn btn-secondary" onClick={getAIInsights} disabled={aiLoading}>
              {aiLoading ? 'Analyzing...' : '✦ AI Insights'}
            </button>
          </div>

          {aiInsight && (
            <div className="panel" style={{ marginBottom: 12, borderColor: 'rgba(0,212,180,0.3)' }}>
              <div className="panel-title">AI ANALYSIS</div>
              <p style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{aiInsight}</p>
            </div>
          )}

          <div className="card-grid">
            {results.results.map((r, i) => <RepoCard key={i} repo={r} />)}
          </div>

          <div className="pagination">
            <button className="btn btn-secondary" onClick={() => doSearch(page - 1)} disabled={!pg?.has_prev || loading}>
              <ChevronLeft size={13} />
            </button>
            <span>Page {pg?.current_page} of {pg?.total_pages}</span>
            <button className="btn btn-secondary" onClick={() => doSearch(page + 1)} disabled={!pg?.has_next || loading}>
              <ChevronRight size={13} />
            </button>
          </div>
        </>
      )}

      {!results && !loading && !error && (
        <div className="empty-state">
          <Search size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
          <div>Enter a query above to search repositories</div>
        </div>
      )}

      {loading && (
        <div className="loading"><div className="spinner" /> Querying GitHub index...</div>
      )}
    </div>
  )
}
