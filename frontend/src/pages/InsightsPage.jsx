import { useState, useEffect } from 'react'
import { Brain, Zap, MessageSquare, Search } from 'lucide-react'
import { insights } from '../api'

export default function InsightsPage() {
  const [tab, setTab]           = useState('query')
  const [health, setHealth]     = useState(null)
  const [query, setQuery]       = useState('')
  const [answer, setAnswer]     = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState(null)
  const [analyzeJson, setAnalyzeJson] = useState('[]')
  const [analysisType, setAnalysisType] = useState('general')
  const [analysisResult, setAnalysisResult] = useState(null)

  useEffect(() => {
    insights.health()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable' }))
  }, [])

  async function doQuery() {
    if (!query.trim()) return
    setLoading(true); setAnswer(''); setError(null)
    try {
      const data = await insights.query({ query })
      setAnswer(data.answer)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doAnalyze() {
    setLoading(true); setAnalysisResult(null); setError(null)
    try {
      const repoList = JSON.parse(analyzeJson)
      const data = await insights.analyze({ repositories: repoList, analysis_type: analysisType })
      setAnalysisResult(data)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const nimOk = health?.nim_configured

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">AI INSIGHTS</div>
        <div className="page-sub">NVIDIA NIM — natural language OSINT analysis</div>
      </div>

      {health && (
        <div className="panel" style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
          <span className={`badge ${health.status === 'healthy' ? 'badge-green' : 'badge-red'}`}>
            {health.status?.toUpperCase()}
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            NIM: <span style={{ color: nimOk ? 'var(--accent)' : 'var(--warn)' }}>
              {nimOk ? 'CONFIGURED' : 'FALLBACK MODE'}
            </span>
          </span>
          {health.rate_limit && (
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              Rate limit: {health.rate_limit.available_slots}/{health.rate_limit_per_minute} slots available
            </span>
          )}
          {!nimOk && (
            <span className="badge badge-yellow">Set NIM_API_KEY in .env to enable AI</span>
          )}
        </div>
      )}

      <div className="tabs">
        {[['query','Natural Language'],['analyze','Analyze Repos']].map(([k, l]) => (
          <button key={k} className={`tab ${tab === k ? 'active' : ''}`} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>

      {tab === 'query' && (
        <div className="panel">
          <div className="panel-title">ASK ANYTHING ABOUT YOUR OSINT DATA</div>
          <div className="form-row" style={{ marginBottom: 12 }}>
            <textarea
              className="form-input"
              style={{ minWidth: 'unset', flex: 1, height: 80, resize: 'vertical' }}
              placeholder="e.g. What are the most popular Python OSINT tools? What patterns do you see in these repositories?"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={doQuery} disabled={loading || !query.trim()}>
            <MessageSquare size={13} /> {loading ? 'Querying NIM...' : 'Ask NIM'}
          </button>

          {error && <div className="error-box" style={{ marginTop: 12 }}>{error}</div>}

          {answer && (
            <div style={{ marginTop: 16 }}>
              <div className="panel-title">RESPONSE</div>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', lineHeight: 1.8, whiteSpace: 'pre-wrap', background: 'var(--bg-card)', padding: 14, borderRadius: 6, border: '1px solid var(--border)' }}>
                {answer}
              </div>
            </div>
          )}

          {loading && <div className="loading" style={{ marginTop: 12 }}><div className="spinner" /> Waiting for NIM response...</div>}
        </div>
      )}

      {tab === 'analyze' && (
        <div className="panel">
          <div className="panel-title">ANALYZE REPOSITORY LIST</div>
          <div className="form-group" style={{ marginBottom: 12 }}>
            <label className="form-label">Analysis Type</label>
            <select className="form-select" style={{ width: 200 }} value={analysisType} onChange={e => setAnalysisType(e.target.value)}>
              <option value="general">General</option>
              <option value="security">Security</option>
              <option value="trends">Trends</option>
              <option value="contributors">Contributors</option>
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 12 }}>
            <label className="form-label">Repositories JSON (array)</label>
            <textarea
              className="form-input code-block"
              style={{ minWidth: 'unset', width: '100%', height: 120, resize: 'vertical', background: 'var(--bg-base)' }}
              value={analyzeJson}
              onChange={e => setAnalyzeJson(e.target.value)}
              placeholder='[{"name": "repo", "description": "...", "stargazers_count": 100}]'
            />
          </div>
          <button className="btn btn-primary" onClick={doAnalyze} disabled={loading}>
            <Brain size={13} /> {loading ? 'Analyzing...' : 'Analyze'}
          </button>

          {error && <div className="error-box" style={{ marginTop: 12 }}>{error}</div>}

          {analysisResult && (
            <div style={{ marginTop: 16 }}>
              <div className="panel-title">ANALYSIS RESULT</div>
              <div className="code-block">{JSON.stringify(analysisResult, null, 2)}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
