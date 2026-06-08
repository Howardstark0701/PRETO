import { useState, useEffect } from 'react'
import { Brain, MessageSquare, Activity, AlertTriangle, Map } from 'lucide-react'
import { insights } from '../api'

const DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"

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
        {[['query','QUERY_ENGINE'],['analyze','REPO_ANALYZER'],['signals','SIGNAL_LOG'],['geo','GEOSPATIAL']].map(([k, l]) => (
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

      {/* ── Signal Log Tab ── */}
      {tab === 'signals' && (
        <div className="panel">
          <div className="panel-header"><AlertTriangle size={11} /> PREDICTIVE_ALERT_LOG</div>
          <table className="data-table">
            <thead>
              <tr><th>TIMESTAMP</th><th>SIGNAL</th><th>SEVERITY</th><th>SOURCE</th><th>STATUS</th></tr>
            </thead>
            <tbody>
              <tr><td style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>—</td><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 11 }}>NO SIGNALS DETECTED</td></tr>
            </tbody>
          </table>
        </div>
      )}

      {/* ── Geospatial Tab ── */}
      {tab === 'geo' && (
        <div className="panel">
          <div className="panel-header"><Map size={11} /> GEOSPATIAL_OVERLAY</div>
          <div className="empty-state">
            <Map size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
            <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1, fontSize: 11 }}>GEOSPATIAL MAP UNAVAILABLE</div>
            <div style={{ fontSize: 10, marginTop: 6, color: 'var(--text-muted)' }}>Map visualization requires backend integration</div>
          </div>
        </div>
      )}
    </div>
  )
}
