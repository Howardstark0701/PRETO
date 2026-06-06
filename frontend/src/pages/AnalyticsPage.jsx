import { useState } from 'react'
import { BarChart2, TrendingUp, Download } from 'lucide-react'
import { advanced } from '../api'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, PieChart, Pie, Legend
} from 'recharts'

const COLORS = ['#00d4b4','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#10b981','#f97316','#06b6d4']

const DEMO_REPOS = [
  { name: 'osint-tool', stargazers_count: 2300, forks_count: 430, language: 'Python', created_at: '2023-01-15' },
  { name: 'recon-ng',   stargazers_count: 5100, forks_count: 980, language: 'Python', created_at: '2022-06-01' },
  { name: 'maltego',    stargazers_count: 1200, forks_count: 210, language: 'Java',   created_at: '2023-08-20' },
  { name: 'shodan-cli', stargazers_count: 3400, forks_count: 670, language: 'Python', created_at: '2022-11-10' },
  { name: 'spiderfoot', stargazers_count: 9800, forks_count: 1800, language: 'Python', created_at: '2021-04-05' },
]

export default function AnalyticsPage() {
  const [reposJson, setReposJson] = useState(JSON.stringify(DEMO_REPOS, null, 2))
  const [analytics, setAnalytics] = useState(null)
  const [trends, setTrends]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [exportFmt, setExportFmt] = useState('json')
  const [tab, setTab]             = useState('analytics')

  async function doAnalytics() {
    setLoading(true); setError(null)
    try {
      const repoList = JSON.parse(reposJson)
      const data = await advanced.analytics({ repositories: repoList, period_days: 30 })
      setAnalytics(data.analytics)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doTrends() {
    setLoading(true); setError(null)
    try {
      const data = await advanced.searchTrends(10)
      setTrends(data.trends)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doExport() {
    setLoading(true); setError(null)
    try {
      const repoList = JSON.parse(reposJson)

      if (exportFmt === 'pdf') {
        const blob = await advanced.exportPdf(repoList)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a'); a.href = url
        a.download = 'preto-report.pdf'; a.click()
        URL.revokeObjectURL(url)
      } else {
        const data = await advanced.export({ repositories: repoList, format: exportFmt })
        const blob = new Blob(
          [typeof data.data === 'string' ? data.data : JSON.stringify(data.data, null, 2)],
          { type: exportFmt === 'csv' ? 'text/csv' : 'application/json' }
        )
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a'); a.href = url
        a.download = `preto-export.${exportFmt}`; a.click()
        URL.revokeObjectURL(url)
      }
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  // Build chart data from analytics or demo
  const repos = (() => { try { return JSON.parse(reposJson) } catch { return [] } })()
  const starData = repos.map(r => ({ name: r.name, stars: r.stargazers_count, forks: r.forks_count }))
  const langMap  = repos.reduce((acc, r) => { if (r.language) acc[r.language] = (acc[r.language] || 0) + 1; return acc }, {})
  const langData = Object.entries(langMap).map(([name, value]) => ({ name, value }))

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">ANALYTICS</div>
        <div className="page-sub">Repository intelligence and trend analysis</div>
      </div>

      <div className="tabs">
        {[['analytics','Analysis'],['trends','Search Trends'],['export','Export']].map(([k,l]) => (
          <button key={k} className={`tab ${tab===k?'active':''}`} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>

      {tab === 'analytics' && (
        <>
          <div className="panel" style={{ marginBottom: 16 }}>
            <div className="panel-title">REPOSITORY DATA (JSON)</div>
            <textarea
              className="form-input code-block"
              style={{ width: '100%', height: 120, resize: 'vertical', background: 'var(--bg-base)', minWidth: 'unset', marginBottom: 10 }}
              value={reposJson}
              onChange={e => setReposJson(e.target.value)}
            />
            <button className="btn btn-primary" onClick={doAnalytics} disabled={loading}>
              <BarChart2 size={13} /> {loading ? 'Analyzing...' : 'Run Analytics'}
            </button>
          </div>

          {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}

          <div style={{ display: 'grid', gap: 16, gridTemplateColumns: '1fr 1fr' }}>
            <div className="panel">
              <div className="panel-title">STARS vs FORKS</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={starData} margin={{ top: 0, right: 0, bottom: 20, left: -20 }}>
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 9 }} angle={-20} textAnchor="end" />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 9 }} />
                  <Tooltip contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 11 }} cursor={{ fill: 'rgba(0,212,180,0.05)' }} />
                  <Bar dataKey="stars" fill="#00d4b4" radius={[3,3,0,0]} />
                  <Bar dataKey="forks" fill="#3b82f6" radius={[3,3,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="panel">
              <div className="panel-title">LANGUAGE BREAKDOWN</div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={langData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`} labelLine={false} style={{ fontSize: 9 }}>
                    {langData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {analytics && (
            <div className="panel" style={{ marginTop: 16 }}>
              <div className="panel-title">API ANALYTICS RESULT</div>
              <div className="code-block">{JSON.stringify(analytics, null, 2)}</div>
            </div>
          )}
        </>
      )}

      {tab === 'trends' && (
        <div className="panel">
          <div className="panel-title">TOP SEARCH TRENDS</div>
          <button className="btn btn-primary" style={{ marginBottom: 16 }} onClick={doTrends} disabled={loading}>
            <TrendingUp size={13} /> {loading ? 'Loading...' : 'Fetch Trends'}
          </button>
          {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}
          {trends && (
            trends.length > 0
              ? <table className="data-table">
                  <thead><tr><th>#</th><th>Query</th></tr></thead>
                  <tbody>{trends.map((t, i) => (
                    <tr key={i}><td>{i + 1}</td><td>{t}</td></tr>
                  ))}</tbody>
                </table>
              : <div className="empty-state">No search trends yet — start searching to build history</div>
          )}
          {!trends && !loading && <div className="empty-state">Click "Fetch Trends" to load trending searches</div>}
        </div>
      )}

      {tab === 'export' && (
        <div className="panel">
          <div className="panel-title">EXPORT REPOSITORY DATA</div>
          <div className="form-row" style={{ marginBottom: 16 }}>
            <div className="form-group">
              <label className="form-label">Format</label>
              <select className="form-select" value={exportFmt} onChange={e => setExportFmt(e.target.value)}>
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
                <option value="pdf">PDF Report</option>
              </select>
            </div>
            <button className="btn btn-primary" onClick={doExport} disabled={loading}>
              <Download size={13} /> {loading ? 'Exporting...' : `Export ${exportFmt.toUpperCase()}`}
            </button>
          </div>
          <div className="form-group">
            <label className="form-label">Data to export (edit above in Analytics tab or paste here)</label>
            <textarea
              className="form-input code-block"
              style={{ width: '100%', height: 160, resize: 'vertical', background: 'var(--bg-base)', minWidth: 'unset' }}
              value={reposJson}
              onChange={e => setReposJson(e.target.value)}
            />
          </div>
          {error && <div className="error-box" style={{ marginTop: 12 }}>{error}</div>}
        </div>
      )}
    </div>
  )
}
