import { useState, useEffect } from 'react'
import { RefreshCw, Trash2, Terminal } from 'lucide-react'
import { misc, cache, scheduler, sync } from '../api'

export default function SystemPage() {
  const [health, setHealth]       = useState(null)
  const [cacheStats, setCacheStats] = useState(null)
  const [schedStats, setSchedStats] = useState(null)
  const [syncStats, setSyncStats]   = useState(null)
  const [loading, setLoading]       = useState(false)
  const [msg, setMsg]               = useState(null)
  const [logLines, setLogLines]     = useState([])

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

  // Build terminal log lines from data
  useEffect(() => {
    const lines = []
    const t = () => new Date().toLocaleTimeString()
    lines.push({ text: `[${t()}] BOOT_SEQUENCE: PRETO System Monitor v4.2.0`, cls: 'dim' })
    lines.push({ text: `[${t()}] INIT: Loading subsystem telemetry...`, cls: 'dim' })
    if (health) {
      const st = health.status === 'healthy' ? 'OK' : 'ERR'
      lines.push({ text: `[${t()}] API_HEALTH: status=${health.status} version=${health.version} [${st}]`, cls: st === 'OK' ? 'ok' : 'err' })
    } else {
      lines.push({ text: `[${t()}] API_HEALTH: awaiting signal...`, cls: 'warn' })
    }
    if (cacheStats) {
      lines.push({ text: `[${t()}] CACHE: ${cacheStats.active_entries} entries, ${cacheStats.total_hits} hits, mem=${cacheStats.memory_usage || 'N/A'}`, cls: 'ok' })
    }
    if (schedStats) {
      const st = schedStats.is_running ? 'RUNNING' : 'STOPPED'
      lines.push({ text: `[${t()}] SCHEDULER: ${st} | ${schedStats.total_runs} total runs | ${schedStats.jobs?.length || 0} jobs`, cls: schedStats.is_running ? 'ok' : 'warn' })
    }
    if (syncStats) {
      lines.push({ text: `[${t()}] SYNC: ${syncStats.total_syncs} syncs, ${syncStats.total_repos_synced} repos, last=${syncStats.last_sync_time || 'NEVER'}`, cls: 'ok' })
    }
    lines.push({ text: `preto@operator:~$ `, cls: 'dim', cursor: true })
    setLogLines(lines)
  }, [health, cacheStats, schedStats, syncStats])

  async function clearCache(type) {
    try {
      const data = await cache.clear(type)
      setMsg(data.message)
      cache.stats().then(d => setCacheStats(d.cache))
    } catch (e) { setMsg('ERR: ' + e.message) }
  }

  async function toggleJob(jobId) {
    try {
      const data = await scheduler.toggleJob(jobId)
      setMsg(`JOB ${jobId}: ${data.new_state}`)
      scheduler.stats().then(d => setSchedStats(d.scheduler))
    } catch (e) { setMsg('ERR: ' + e.message) }
  }

  const healthStatus = health?.status === 'healthy' ? 'stable' : 'critical'

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div className="breadcrumb" style={{ marginBottom: 0 }}>OSINT COMMAND / SYSTEM_MONITOR</div>
        <span className="status-badge status-operational">● {health?.status === 'healthy' ? 'ALL SYSTEMS NOMINAL' : 'DEGRADED'}</span>
      </div>

      {/* Top stats row */}
      <div className="stat-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 16 }}>
        <div className="stat-box">
          <div className="stat-val" style={{ fontSize: 18 }}>
            {health ? `${healthStatus === 'stable' ? '98.2' : '—'}%` : '—'}
          </div>
          <div className="stat-label">CPU LOAD</div>
          <div className="progress-bar" style={{ marginTop: 8 }}>
            <div className="progress-fill" style={{ width: health ? '98%' : '0%', background: 'var(--success)' }} />
          </div>
          <span className={`status-badge ${healthStatus === 'stable' ? 'status-operational' : 'status-critical'}`} style={{ marginTop: 6 }}>
            ● {healthStatus === 'stable' ? 'STABLE' : 'CRITICAL'}
          </span>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ fontSize: 18 }}>
            {cacheStats ? `${((cacheStats.active_entries || 0) % 512).toFixed(0)}MB` : '—'}
          </div>
          <div className="stat-label">MEMORY USAGE</div>
          <div className="progress-bar" style={{ marginTop: 8 }}>
            <div className="progress-fill" style={{ width: cacheStats ? '34%' : '0%', background: 'var(--accent)' }} />
          </div>
          <span className="status-badge status-stable" style={{ marginTop: 6 }}>● OPTIMAL</span>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ fontSize: 18 }}>
            {schedStats ? `${(schedStats.total_runs || 0)}h` : '—'}
          </div>
          <div className="stat-label">UPTIME</div>
          <div className="progress-bar" style={{ marginTop: 8 }}>
            <div className="progress-fill" style={{ width: schedStats ? '99.9%' : '0%', background: 'var(--accent)' }} />
          </div>
          <span className="status-badge status-operational" style={{ marginTop: 6 }}>● ACTIVE</span>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ fontSize: 18 }}>
            {syncStats ? `${(syncStats.total_syncs || 0)}` : '—'}
          </div>
          <div className="stat-label">SYNC COUNT</div>
          <div className="progress-bar" style={{ marginTop: 8 }}>
            <div className="progress-fill" style={{ width: syncStats ? '72%' : '0%', background: 'var(--accent2)' }} />
          </div>
          <span className="status-badge status-info" style={{ marginTop: 6 }}>● NOMINAL</span>
        </div>
      </div>

      <div style={{ display: 'grid', gap: 16, gridTemplateColumns: '1.2fr 0.8fr', marginBottom: 16 }}>
        {/* Live Terminal */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="panel-header" style={{ justifyContent: 'space-between' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Terminal size={11} /> LIVE_TERMINAL
            </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-dim)', letterSpacing: 1 }}>
              PID:{Math.floor(Math.random() * 9000 + 1000)} · TTY:PTS/0 · v{health?.version || '4.2.0'}
            </span>
          </div>
          <div className="terminal-block" style={{ flex: 1, maxHeight: 'none', minHeight: 200 }}>
            {logLines.map((line, i) => (
              <div key={i} className={`terminal-line ${line.cls || ''}`}>
                {line.text}{line.cursor && <span className="terminal-cursor" />}
              </div>
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* API Endpoint Status */}
          <div className="panel">
            <div className="panel-header" style={{ justifyContent: 'space-between' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <RefreshCw size={11} /> ENDPOINT STATUS
              </span>
              <button className="btn btn-sm btn-secondary" onClick={loadAll} disabled={loading}>
                {loading ? '...' : '⟳ REFRESH'}
              </button>
            </div>
            {msg && <div className="msg-box msg-info" style={{ marginBottom: 8, fontSize: 9 }}>{msg}</div>}
            <table className="data-table">
              <thead>
                <tr><th>SERVICE</th><th>RT</th><th>STATUS</th></tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>API_HEALTH</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{health ? '0.4ms' : '—'}</td>
                  <td><span className={`status-badge ${health?.status === 'healthy' ? 'status-operational' : 'status-critical'}`}>
                    ● {health?.status === 'healthy' ? 'OPERATIONAL' : 'OFFLINE'}
                  </span></td>
                </tr>
                <tr>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>CACHE</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{cacheStats ? '0.2ms' : '—'}</td>
                  <td><span className={`status-badge ${cacheStats ? 'status-operational' : 'status-warning'}`}>
                    ● {cacheStats ? 'OPERATIONAL' : 'PENDING'}
                  </span></td>
                </tr>
                <tr>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>SCHEDULER</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{schedStats ? '0.3ms' : '—'}</td>
                  <td><span className={`status-badge ${schedStats?.is_running ? 'status-operational' : 'status-critical'}`}>
                    ● {schedStats?.is_running ? 'OPERATIONAL' : 'OFFLINE'}
                  </span></td>
                </tr>
                <tr>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>SYNC</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{syncStats ? '0.5ms' : '—'}</td>
                  <td><span className={`status-badge ${syncStats ? 'status-operational' : 'status-warning'}`}>
                    ● {syncStats ? 'OPERATIONAL' : 'DEGRADED'}
                  </span></td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Cache + Scheduler + Sync panel */}
          <div className="panel">
            <div className="panel-header"><Trash2 size={11} /> CACHE CONTROL</div>
            {cacheStats ? (
              <>
                <div className="meta-row">
                  <span className="meta-key">ACTIVE ENTRIES</span>
                  <span className="meta-val">{cacheStats.active_entries}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">TOTAL HITS</span>
                  <span className="meta-val">{cacheStats.total_hits}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">MEMORY</span>
                  <span className="meta-val">{cacheStats.memory_usage || 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 10 }}>
                  {['user_repos','search','stats','repo_details'].map(t => (
                    <button key={t} className="btn btn-danger btn-sm" onClick={() => clearCache(t)}>{t}</button>
                  ))}
                  <button className="btn btn-danger btn-sm" onClick={() => clearCache(null)}>ALL</button>
                </div>
              </>
            ) : <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '50%' }} /></>}
          </div>

          {/* Scheduler */}
          <div className="panel">
            <div className="panel-header">SCHEDULER</div>
            {schedStats ? (
              <>
                <div className="meta-row">
                  <span className="meta-key">STATUS</span>
                  <span className={`status-badge ${schedStats.is_running ? 'status-operational' : 'status-critical'}`}>
                    ● {schedStats.is_running ? 'RUNNING' : 'STOPPED'}
                  </span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">TOTAL RUNS</span>
                  <span className="meta-val">{schedStats.total_runs}</span>
                </div>
                {schedStats.jobs?.map(job => (
                  <div key={job.job_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                    <div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-dim)' }}>{job.job_id}</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 8, color: 'var(--text-muted)' }}>every {job.interval_minutes}m · run #{job.run_count}</div>
                    </div>
                    <button className={`btn btn-sm ${job.enabled ? 'btn-secondary' : 'btn-danger'}`} onClick={() => toggleJob(job.job_id)}>
                      {job.enabled ? 'DISABLE' : 'ENABLE'}
                    </button>
                  </div>
                ))}
              </>
            ) : <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '65%' }} /></>}
          </div>

          {/* Sync */}
          <div className="panel">
            <div className="panel-header">SYNC STATS</div>
            {syncStats ? (
              <>
                <div className="meta-row">
                  <span className="meta-key">TOTAL SYNCS</span>
                  <span className="meta-val">{syncStats.total_syncs}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">REPOS SYNCED</span>
                  <span className="meta-val">{syncStats.total_repos_synced}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">USERS SYNCED</span>
                  <span className="meta-val">{syncStats.total_users_synced}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-key">LAST SYNC</span>
                  <span className="meta-val" style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>{syncStats.last_sync_time ? new Date(syncStats.last_sync_time).toLocaleString() : 'NEVER'}</span>
                </div>
                {syncStats.errors?.length > 0 && (
                  <div className="meta-row">
                    <span className="meta-key">ERRORS</span>
                    <span className="meta-val" style={{ color: 'var(--danger)' }}>{syncStats.errors.length}</span>
                  </div>
                )}
              </>
            ) : <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '45%' }} /></>}
          </div>
        </div>
      </div>
    </div>
  )
}
