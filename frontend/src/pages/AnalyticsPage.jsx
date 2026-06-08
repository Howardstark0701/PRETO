import { useState } from 'react'
import { BarChart2, TrendingUp, Download, Activity, Zap, Radio } from 'lucide-react'
import { advanced } from '../api'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, PieChart, Pie
} from 'recharts'

const COLORS = ['#00d4b4','#3b82f6','#f59e0b','#ef4444','#8b5cf6','#10b981','#f97316','#06b6d4']

const DEMO_REPOS = [
  { name: 'osint-tool', stargazers_count: 2300, forks_count: 430, language: 'Python', created_at: '2023-01-15' },
  { name: 'recon-ng',   stargazers_count: 5100, forks_count: 980, language: 'Python', created_at: '2022-06-01' },
  { name: 'maltego',    stargazers_count: 1200, forks_count: 210, language: 'Java',   created_at: '2023-08-20' },
  { name: 'shodan-cli', stargazers_count: 3400, forks_count: 670, language: 'Python', created_at: '2022-11-10' },
  { name: 'spiderfoot', stargazers_count: 9800, forks_count: 1800, language: 'Python', created_at: '2021-04-05' },
]

const signalVolumeData = [
  { month: 'JAN', signals: 45 }, { month: 'FEB', signals: 52 }, { month: 'MAR', signals: 38 },
  { month: 'APR', signals: 65 }, { month: 'MAY', signals: 71 }, { month: 'JUN', signals: 59 },
]

const MONO_TICK = { fontFamily: 'var(--font-mono)', fontSize: 9, fill: 'var(--text-muted)' }
const TOOLTIP_STYLE = { background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 10, borderRadius: 0 }

export default function AnalyticsPage() {
  const [tab, setTab]           = useState('volume')
  const [reposJson, setReposJson] = useState(JSON.stringify(DEMO_REPOS, null, 2))
  const [analytics, setAnalytics] = useState(null)
  const [trends, setTrends]       = useState(null)
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  const [exportFmt, setExportFmt] = useState('json')

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

  const repos = (() => { try { return JSON.parse(reposJson) } catch { return [] } })()
  const starData = repos.map(r => ({ name: r.name, stars: r.stargazers_count, forks: r.forks_count }))
  const langMap  = repos.reduce((acc, r) => { if (r.language) acc[r.language] = (acc[r.language] || 0) + 1; return acc }, {})
  const langData = Object.entries(langMap).map(([name, value]) => ({ name, value }))
  const topAssets = [...repos].sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0))

  return (
    <div className="page">
      <div className="breadcrumb">OSINT COMMAND / ANALYTICS</div>

      <div className="mode-b-tabs">
        {[['volume','SIGNAL_VOLUME'],['assets','TOP_ASSETS'],['telemetry','TELEMETRY'],['trends','TRENDS'],['export','EXPORT']].map(([k, l]) => (
          <button key={k} className={`mode-b-tab ${tab === k ? 'active' : ''}`} onClick={() => setTab(k)}>{l}</button>
        ))}
      </div>

      {error && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{error}</div>}

      {/* ── Signal Volume ── */}
      {tab === 'volume' && (
        <>
          <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 1fr', marginBottom: 12 }}>
            <div className="panel">
              <div className="panel-header"><Activity size={11} /> SIGNAL_VOLUME (6-MONTH)</div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={signalVolumeData} margin={{ top: 6, right: 12, bottom: 6, left: -20 }}>
                  <XAxis dataKey="month" tick={MONO_TICK} stroke="#1f2d45" />
                  <YAxis tick={MONO_TICK} stroke="#1f2d45" />
                  <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#94a3b8' }} cursor={{ stroke: 'rgba(0,212,180,0.2)' }} />
                  <Line type="monotone" dataKey="signals" stroke="#00d4b4" strokeWidth={2} dot={{ fill: '#00d4b4', r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
              <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                <span className="status-badge status-stable" style={{ fontSize: 8 }}>PEAK: 71</span>
                <span className="status-badge status-info" style={{ fontSize: 8 }}>AVG: 55</span>
                <span className="status-badge status-warning" style={{ fontSize: 8 }}>TREND: +8.3%</span>
              </div>
            </div>
            <div className="panel">
              <div className="panel-header"><BarChart2 size={11} /> LANGUAGE_BREAKDOWN</div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={langData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70}
                    label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
                    labelLine={false} style={{ fontSize: 9, fontFamily: 'var(--font-mono)' }}>
                    {langData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header"><BarChart2 size={11} /> STARS vs FORKS</div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={starData} margin={{ top: 0, right: 0, bottom: 20, left: -20 }}>
                <XAxis dataKey="name" tick={MONO_TICK} angle={-20} textAnchor="end" stroke="#1f2d45" />
                <YAxis tick={MONO_TICK} stroke="#1f2d45" />
                <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: '#94a3b8' }} cursor={{ fill: 'rgba(0,212,180,0.05)' }} />
                <Bar dataKey="stars" fill="#00d4b4" radius={[0,0,0,0]} />
                <Bar dataKey="forks" fill="#3b82f6" radius={[0,0,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="panel" style={{ marginTop: 12 }}>
            <div className="panel-header"><BarChart2 size={11} /> REPOSITORY_DATA_INPUT</div>
            <textarea
              className="form-input"
              style={{ width: '100%', height: 100, resize: 'vertical', background: 'var(--bg-terminal)', minWidth: 'unset', fontFamily: 'var(--font-mono)', fontSize: 11, marginBottom: 10 }}
              value={reposJson}
              onChange={e => setReposJson(e.target.value)}
            />
            <button className="btn btn-primary btn-sm" onClick={doAnalytics} disabled={loading}>
              <BarChart2 size={11} /> {loading ? '⟳ PROCESSING...' : '▼ RUN ANALYTICS'}
            </button>
            {analytics && (
              <div className="terminal-block" style={{ marginTop: 10, maxHeight: 200 }}>
                {JSON.stringify(analytics, null, 2)}
              </div>
            )}
          </div>
        </>
      )}

      {/* ── Top Assets ── */}
      {tab === 'assets' && (
        <div className="panel">
          <div className="panel-header"><Zap size={11} /> TOP PERFORMING ASSETS</div>
          {topAssets.length > 0 ? (
            <table className="data-table">
              <thead><tr><th>#</th><th>NAME</th><th>STARS</th><th>FORKS</th><th>LANGUAGE</th><th>CONFIDENCE</th></tr></thead>
              <tbody>
                {topAssets.map((r, i) => {
                  const conf = Math.min(99, (r.stargazers_count || 0) > 1000 ? 85 + Math.floor(Math.random() * 14) : 50 + Math.floor(Math.random() * 30))
                  return (
                    <tr key={i}>
                      <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{(i + 1).toString().padStart(2, '0')}</td>
                      <td style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', fontSize: 11 }}>{r.name}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>★ {r.stargazers_count?.toLocaleString() || 0}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>⑂ {r.forks_count?.toLocaleString() || 0}</td>
                      <td>{r.language && <span className="status-badge status-info" style={{ fontSize: 8, padding: '1px 5px' }}>{r.language}</span>}</td>
                      <td><span className={`status-badge ${conf > 80 ? 'status-operational' : 'status-warning'}`} style={{ fontSize: 8, padding: '1px 5px' }}>{conf}%</span></td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          ) : <div className="empty-state">NO ASSET DATA — ENTER REPOSITORY JSON IN SIGNAL_VOLUME TAB</div>}
        </div>
      )}

      {/* ── Live Telemetry ── */}
      {tab === 'telemetry' && (
        <div className="panel">
          <div className="panel-header"><Radio size={11} /> LIVE_TELEMETRY_FEED</div>
          <div className="terminal-block" style={{ minHeight: 250, maxHeight: 400 }}>
            {[
              { text: `[${new Date().toLocaleTimeString()}] TELEMETRY INIT: PRETO Analytics v4.2.0`, cls: 'dim' },
              { text: `[${new Date().toLocaleTimeString()}] SIGNAL: ${repos.length} assets loaded`, cls: 'ok' },
              { text: `[${new Date().toLocaleTimeString()}] VOLUME: ${signalVolumeData.reduce((s, d) => s + d.signals, 0)} total signals`, cls: 'ok' },
              { text: `[${new Date().toLocaleTimeString()}] TOP: ${topAssets[0]?.name || 'N/A'} (★${topAssets[0]?.stargazers_count || 0})`, cls: 'ok' },
              { text: `[${new Date().toLocaleTimeString()}] LANG: ${Object.keys(langMap).length} languages detected`, cls: 'dim' },
              { text: `[${new Date().toLocaleTimeString()}] EXPORT: Ready`, cls: 'dim' },
              { text: `preto@analytics:~$ `, cls: 'dim', cursor: true },
            ].map((line, i) => (
              <div key={i} className={`terminal-line ${line.cls || ''}`}>
                {line.text}{line.cursor && <span className="terminal-cursor" />}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Trends ── */}
      {tab === 'trends' && (
        <div className="panel">
          <div className="panel-header"><TrendingUp size={11} /> SEARCH_TRENDS</div>
          <button className="btn btn-primary btn-sm" style={{ marginBottom: 12 }} onClick={doTrends} disabled={loading}>
            <TrendingUp size={11} /> {loading ? '⟳ FETCHING...' : '▼ FETCH TRENDS'}
          </button>
          {trends?.length > 0 ? (
            <table className="data-table">
              <thead><tr><th>#</th><th>QUERY</th></tr></thead>
              <tbody>{trends.map((t, i) => (
                <tr key={i}><td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{(i+1).toString().padStart(2,'0')}</td><td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>{t}</td></tr>
              ))}</tbody>
            </table>
          ) : !loading ? <div className="empty-state">NO TRENDS — START SEARCHING TO BUILD HISTORY</div> : null}
        </div>
      )}

      {/* ── Export ── */}
      {tab === 'export' && (
        <div className="panel">
          <div className="panel-header"><Download size={11} /> EXPORT_DATA</div>
          <div className="form-row" style={{ marginBottom: 12 }}>
            <div className="form-group">
              <label className="form-label">FORMAT</label>
              <select className="form-select" style={{ fontSize: 11 }} value={exportFmt} onChange={e => setExportFmt(e.target.value)}>
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
                <option value="pdf">PDF REPORT</option>
              </select>
            </div>
            <button className="btn btn-primary btn-sm" style={{ marginTop: 16 }} onClick={doExport} disabled={loading}>
              <Download size={11} /> {loading ? '⟳ EXPORTING...' : '▼ EXPORT'}
            </button>
          </div>
          <div className="form-group">
            <label className="form-label">DATA PAYLOAD</label>
            <textarea
              className="form-input"
              style={{ width: '100%', height: 160, resize: 'vertical', background: 'var(--bg-terminal)', minWidth: 'unset', fontFamily: 'var(--font-mono)', fontSize: 11 }}
              value={reposJson}
              onChange={e => setReposJson(e.target.value)}
            />
          </div>
        </div>
      )}
    </div>
  )
}
