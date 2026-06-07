import { useState, useEffect } from 'react'
import { Settings, Database, Clock, Zap, RefreshCw, Trash2 } from 'lucide-react'
import { misc, cache, scheduler, sync } from '../api'

export default function SystemPage() {
  const [health, setHealth]       = useState(null)
  const [cacheStats, setCacheStats] = useState(null)
  const [schedStats, setSchedStats] = useState(null)
  const [syncStats, setSyncStats]   = useState(null)
  const [loading, setLoading]       = useState(false)
  const [msg, setMsg]               = useState(null)

  async function loadAll() {
    setLoading(true)
    try {
      const [h, c, sc, sy] = await Promise.allSettled([
        misc.health(), cache.stats(), scheduler.stats(), sync.stats()
      ])
      if (h.status === 'fulfilled') setHealth(h.value)
      if (c.status === 'fulfilled') setCacheStats(c.value.cache)
      if (sc.status === 'fulfilled') setSchedStats(sc.value.scheduler)
      if (sy.status === 'fulfilled') setSyncStats(sy.value.sync)
    } finally { setLoading(false) }
  }

  useEffect(() => { loadAll() }, [])

  async function clearCache(type) {
    try {
      const data = await cache.clear(type)
      setMsg(data.message)
      cache.stats().then(d => setCacheStats(d.cache))
    } catch (e) { setMsg('Error: ' + e.message) }
  }

  async function toggleJob(jobId) {
    try {
      const data = await scheduler.toggleJob(jobId)
      setMsg(`Job ${jobId}: ${data.new_state}`)
      scheduler.stats().then(d => setSchedStats(d.scheduler))
    } catch (e) { setMsg('Error: ' + e.message) }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">SYSTEM STATUS</div>
        <div className="page-sub">Cache, scheduler, sync — live monitoring</div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <button className="btn btn-secondary" onClick={loadAll} disabled={loading}>
          <RefreshCw size={13} /> {loading ? 'Refreshing...' : 'Refresh All'}
        </button>
        {msg && <div style={{ padding: '8px 12px', background: 'rgba(0,212,180,0.1)', borderRadius: 4, fontSize: 12, color: 'var(--accent)' }}>{msg}</div>}
      </div>

      <div style={{ display: 'grid', gap: 16, gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>

        {/* API Health */}
        <div className="panel">
          <div className="panel-title"><Zap size={11} style={{ display:'inline', marginRight:5 }}/>API HEALTH</div>
          {health ? (
            <>
              <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
                <span className={`badge ${health.status === 'healthy' ? 'badge-green' : 'badge-red'}`}>{health.status?.toUpperCase()}</span>
                <span className="badge badge-blue">v{health.version}</span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {new Date(health.timestamp).toLocaleString()}
              </div>
            </>
          ) : <><div className="skeleton skeleton-text" style={{ width: '50%' }} /><div className="skeleton skeleton-line" style={{ width: '70%', marginTop: 8 }} /></>}
        </div>

        {/* Cache */}
        <div className="panel">
          <div className="panel-title"><Database size={11} style={{ display:'inline', marginRight:5 }}/>CACHE</div>
          {cacheStats ? (
            <>
              <table className="data-table" style={{ marginBottom: 10 }}>
                <tbody>
                  <tr><td>Active entries</td><td style={{ color: 'var(--accent)' }}>{cacheStats.active_entries}</td></tr>
                  <tr><td>Total hits</td><td style={{ color: 'var(--accent)' }}>{cacheStats.total_hits}</td></tr>
                  <tr><td>Memory usage</td><td style={{ color: 'var(--accent)' }}>{cacheStats.memory_usage}</td></tr>
                </tbody>
              </table>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {['user_repos','search','stats','repo_details'].map(t => (
                  <button key={t} className="btn btn-danger" style={{ fontSize: 10, padding: '4px 8px' }} onClick={() => clearCache(t)}>
                    <Trash2 size={10} /> {t}
                  </button>
                ))}
                <button className="btn btn-danger" style={{ fontSize: 10, padding: '4px 8px' }} onClick={() => clearCache(null)}>
                  <Trash2 size={10} /> All
                </button>
              </div>
            </>
          ) : <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '50%' }} /></>}
        </div>

        {/* Scheduler */}
        <div className="panel">
          <div className="panel-title"><Clock size={11} style={{ display:'inline', marginRight:5 }}/>SCHEDULER</div>
          {schedStats ? (
            <>
              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <span className={`badge ${schedStats.is_running ? 'badge-green' : 'badge-red'}`}>
                  {schedStats.is_running ? 'RUNNING' : 'STOPPED'}
                </span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{schedStats.total_runs} runs</span>
              </div>
              {schedStats.jobs?.map(job => (
                <div key={job.job_id} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 12, color: 'var(--text-dim)' }}>{job.job_id}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>every {job.interval_minutes}m · run #{job.run_count}</div>
                  </div>
                  <button
                    className={`btn ${job.enabled ? 'btn-secondary' : 'btn-danger'}`}
                    style={{ fontSize: 10, padding: '3px 8px' }}
                    onClick={() => toggleJob(job.job_id)}
                  >
                    {job.enabled ? 'Disable' : 'Enable'}
                  </button>
                </div>
              ))}
            </>
          ) : <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '65%' }} /></>}
        </div>

        {/* Sync */}
        <div className="panel">
          <div className="panel-title">SYNC STATS</div>
          {syncStats ? (
            <table className="data-table">
              <tbody>
                <tr><td>Total syncs</td><td style={{ color: 'var(--accent)' }}>{syncStats.total_syncs}</td></tr>
                <tr><td>Repos synced</td><td style={{ color: 'var(--accent)' }}>{syncStats.total_repos_synced}</td></tr>
                <tr><td>Users synced</td><td style={{ color: 'var(--accent)' }}>{syncStats.total_users_synced}</td></tr>
                <tr><td>Last sync</td><td style={{ color: 'var(--text-dim)', fontSize: 11 }}>{syncStats.last_sync_time ? new Date(syncStats.last_sync_time).toLocaleString() : 'Never'}</td></tr>
                {syncStats.errors?.length > 0 && (
                  <tr><td>Errors</td><td style={{ color: 'var(--danger)' }}>{syncStats.errors.length}</td></tr>
                )}
              </tbody>
            </table>
          ) : <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '45%' }} /></>}
        </div>


      </div>
    </div>
  )
}
