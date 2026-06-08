import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Shield, LogIn, UserPlus, Key, LogOut, History, Bookmark, Github, Eye, EyeOff, Lock } from 'lucide-react'
import { auth, savedSearches, history, apiKeys } from '../api'

function useGithubCallback(setToken, setUser) {
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (location.pathname !== '/auth/callback') return
    const hash = location.hash.slice(1)
    const params = Object.fromEntries(new URLSearchParams(hash))
    if (params.access_token) {
      localStorage.setItem('preto_token', params.access_token)
      if (params.refresh_token) localStorage.setItem('preto_refresh', params.refresh_token)
      setToken(params.access_token)
      auth.me().then(u => { setUser(u); navigate('/auth', { replace: true }) })
           .catch(() => navigate('/auth', { replace: true }))
    } else {
      navigate('/auth', { replace: true })
    }
  }, [location])
}

export default function AuthPage() {
  const [tab, setTab]       = useState('login')
  const [token, setToken]   = useState(localStorage.getItem('preto_token'))
  const [user, setUser]     = useState(null)
  const [form, setForm]     = useState({ username:'', email:'', password:'', full_name:'' })
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)
  const [msg, setMsg]       = useState(null)
  const [saves, setSaves]   = useState(null)
  const [hist, setHist]     = useState(null)
  const [keys, setKeys]     = useState(null)
  const [ghStatus, setGhStatus] = useState(null)
  const [showPw, setShowPw] = useState(false)
  const [persist, setPersist] = useState(true)

  useGithubCallback(setToken, setUser)

  useEffect(() => {
    if (token) {
      auth.me().then(setUser).catch(() => {
        localStorage.removeItem('preto_token')
        setToken(null)
      })
    }
    auth.githubStatus().then(setGhStatus).catch(() => {})
  }, [token])

  function field(k) {
    return { value: form[k], onChange: e => setForm(f => ({ ...f, [k]: e.target.value })) }
  }

  async function doLogin() {
    setLoading(true); setError(null)
    try {
      const data = await auth.login({ username: form.username, password: form.password })
      localStorage.setItem('preto_token', data.access_token)
      setToken(data.access_token); setUser(data.user)
      setMsg('SESSION INITIALIZED')
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doRegister() {
    setLoading(true); setError(null)
    try {
      await auth.register(form)
      setMsg('OPERATOR REGISTERED. Use login to initialize session.'); setTab('login')
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  function doLogout() {
    localStorage.removeItem('preto_token')
    localStorage.removeItem('preto_refresh')
    setToken(null); setUser(null)
    setSaves(null); setHist(null); setKeys(null)
    setMsg('SESSION TERMINATED')
  }

  async function loadSaves() { try { const d = await savedSearches.list(); setSaves(d.searches) } catch(e) { setError(e.message) } }
  async function loadHist()  { try { const d = await history.list(20); setHist(d.history) }      catch(e) { setError(e.message) } }
  async function loadKeys()  { try { const d = await apiKeys.list(); setKeys(d.keys) }            catch(e) { setError(e.message) } }
  async function clearHist() { try { await history.clear(); setHist([]); setMsg('HISTORY PURGED') } catch(e) { setError(e.message) } }

  async function createKey() {
    const name = window.prompt('API key name:'); if (!name) return
    try {
      const data = await apiKeys.create(name, 100)
      alert(`Key generated (one-time show):\n\n${data.raw_key}`)
      loadKeys()
    } catch(e) { setError(e.message) }
  }

  // ── Authenticated view ──
  if (token && user) return (
    <div className="page">
      <div className="breadcrumb">OSINT COMMAND / OPERATOR_CONSOLE</div>

      <div className="panel" style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
        {user.avatar_url
          ? <img src={user.avatar_url} alt="" style={{ width: 36, height: 36, border: '2px solid var(--accent)' }} />
          : <Shield size={20} style={{ color: 'var(--accent)' }} />
        }
        <div>
          <div style={{ fontWeight: 700, fontFamily: 'var(--font-heading)' }}>{user.username}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{user.email}</div>
          {user.github_login && (
            <div style={{ fontSize: 10, color: 'var(--accent)', marginTop: 2 }}>
              <Github size={10} style={{ display: 'inline', marginRight: 3 }} />
              github.com/{user.github_login}
            </div>
          )}
        </div>
        <span className="status-badge status-operational">● AUTHENTICATED</span>
        {user.github_login && <span className="status-badge status-info">● GITHUB OAUTH</span>}
        <button className="btn btn-danger" style={{ marginLeft: 'auto' }} onClick={doLogout}>
          <LogOut size={13} /> TERMINATE SESSION
        </button>
      </div>

      {msg   && <div className="msg-box msg-info" style={{ marginBottom: 12 }}>{msg}</div>}
      {error && <div className="msg-box msg-error" style={{ marginBottom: 12 }}>{error}</div>}

      <div className="mode-b-tabs">
        {[['saves','SAVED SEARCHES'],['hist','SEARCH HISTORY'],['keys','API KEYS']].map(([k,l]) => (
          <button key={k} className={`mode-b-tab ${tab===k?'active':''}`}
            onClick={() => { setTab(k); if (k==='saves') loadSaves(); if (k==='hist') loadHist(); if (k==='keys') loadKeys() }}>{l}</button>
        ))}
      </div>

      {tab === 'saves' && (
        <div className="panel">
          <div className="panel-header"><Bookmark size={11} /> SAVED SEARCHES</div>
          {saves === null && <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '60%' }} /></>}
          {saves?.length === 0 && <div className="empty-state">NO SAVED SEARCHES</div>}
          {saves?.length > 0 && (
            <table className="data-table">
              <thead><tr><th>QUERY</th><th>LANGUAGE</th><th>FAV</th><th>DATE</th><th></th></tr></thead>
              <tbody>{saves.map(s => (
                <tr key={s.id}>
                  <td style={{ color: 'var(--accent)' }}>{s.query}</td>
                  <td>{s.language || '—'}</td>
                  <td>{s.is_favorite ? '★' : '☆'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>{new Date(s.created_at).toLocaleDateString()}</td>
                  <td style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-secondary btn-sm" onClick={async () => { await savedSearches.favorite(s.id); loadSaves() }}>★</button>
                    <button className="btn btn-danger btn-sm" onClick={async () => { await savedSearches.delete(s.id); loadSaves() }}>DEL</button>
                  </td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'hist' && (
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <div className="panel-header"><History size={11} /> SEARCH HISTORY</div>
            <button className="btn btn-danger btn-sm" onClick={clearHist}>PURGE ALL</button>
          </div>
          {hist === null && <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '50%' }} /></>}
          {hist?.length === 0 && <div className="empty-state">NO HISTORY</div>}
          {hist?.length > 0 && (
            <table className="data-table">
              <thead><tr><th>QUERY</th><th>RESULTS</th><th>CACHE</th><th>TIMESTAMP</th></tr></thead>
              <tbody>{hist.map((h, i) => (
                <tr key={i}>
                  <td>{h.query}</td>
                  <td>{h.results_count}</td>
                  <td><span className={`status-badge ${h.used_cache ? 'status-operational' : 'status-warning'}`}>{h.used_cache ? 'HIT' : 'MISS'}</span></td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>{new Date(h.created_at).toLocaleString()}</td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'keys' && (
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <div className="panel-header"><Key size={11} /> API KEYS</div>
            <button className="btn btn-primary btn-sm" onClick={createKey}>+ GENERATE KEY</button>
          </div>
          {keys === null && <><div className="skeleton skeleton-line" /><div className="skeleton skeleton-line" style={{ width: '45%' }} /></>}
          {keys?.length === 0 && <div className="empty-state">NO API KEYS</div>}
          {keys?.length > 0 && (
            <table className="data-table">
              <thead><tr><th>NAME</th><th>PREFIX</th><th>RATE</th><th>STATUS</th><th>LAST USED</th><th></th></tr></thead>
              <tbody>{keys.map(k => (
                <tr key={k.id}>
                  <td>{k.name}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: 11 }}>{k.prefix}...</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{k.rate_limit}/min</td>
                  <td><span className={`status-badge ${k.is_active ? 'status-operational' : 'status-critical'}`}>{k.is_active ? 'ACTIVE' : 'OFF'}</span></td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: 10 }}>{k.last_used ? new Date(k.last_used).toLocaleDateString() : 'NEVER'}</td>
                  <td style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-secondary btn-sm" onClick={async () => { await apiKeys.toggle(k.id); loadKeys() }}>TOGGLE</button>
                    <button className="btn btn-danger btn-sm" onClick={async () => { await apiKeys.delete(k.id); loadKeys() }}>DEL</button>
                  </td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )

  // ── Login / Register view (Mode B Auth Card) ──
  return (
    <div className="auth-mode-b">
      <div className="auth-card">
        <div className="auth-card-badge"><Lock size={10} /> SECURE-AES256</div>

        <div className="auth-logo">
          <span className="auth-logo-mark">P</span>
        </div>
        <div className="auth-title">OSINT COMMAND</div>
        <div className="auth-subtitle">PRETO Terminal v4.2.0</div>

        <div className="mode-b-tabs" style={{ marginBottom: 20 }}>
          {[['login','LOGIN'],['register','REGISTER']].map(([k,l]) => (
            <button key={k} className={`mode-b-tab ${tab===k?'active':''}`}
              onClick={() => { setTab(k); setError(null); setMsg(null) }}>{l}</button>
          ))}
        </div>

        {error && <div className="msg-box msg-error" style={{ marginBottom: 14 }}>{error}</div>}
        {msg   && <div className="msg-box msg-info" style={{ marginBottom: 14 }}>{msg}</div>}

        {tab === 'login' && (
          <div className="auth-form">
            <div className="auth-field">
              <label className="auth-label">OPERATOR ID</label>
              <input className="auth-input" placeholder="OP-XXXX-XXXX"
                value={form.username} onChange={e => setForm(f => ({...f, username: e.target.value}))}
                onKeyDown={e => e.key==='Enter' && doLogin()} />
            </div>
            <div className="auth-field">
              <label className="auth-label">ACCESS KEY</label>
              <div className="auth-pw-wrap">
                <input className="auth-input" type={showPw ? 'text' : 'password'} placeholder="••••••••"
                  value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))}
                  onKeyDown={e => e.key==='Enter' && doLogin()} />
                <button className="auth-pw-toggle" onClick={() => setShowPw(!showPw)} tabIndex={-1}>
                  {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            <div className="auth-row">
              <label className="auth-checkbox">
                <input type="checkbox" checked={persist} onChange={e => setPersist(e.target.checked)} />
                <span>Persistence Mode</span>
              </label>
              <span className="status-badge status-operational">● NODE: US-EAST-1</span>
            </div>

            <button className="btn btn-primary auth-cta" onClick={doLogin} disabled={loading}>
              <LogIn size={14} /> {loading ? 'INITIALIZING...' : 'INITIALIZE SESSION →'}
            </button>

            <div className="auth-oauth">
              <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center', fontSize: 12 }}
                onClick={() => auth.githubLogin()} disabled={ghStatus && !ghStatus.configured}>
                <Github size={14} /> CONTINUE WITH GITHUB
              </button>
              {ghStatus && !ghStatus.configured && (
                <div style={{ fontSize: 9, color: 'var(--warn)', marginTop: 6, textAlign: 'center' }}>
                  GITHUB OAUTH UNCONFIGURED — ADD CLIENT_ID/SECRET TO .ENV
                </div>
              )}
            </div>

            <div className="auth-footer">
              <span className="auth-footer-item">AUTH_ERR_LOG: 0</span>
              <div className="auth-footer-links">
                <a href="#">Security Policy</a>
                <a href="#">Help</a>
              </div>
            </div>
          </div>
        )}

        {tab === 'register' && (
          <div className="auth-form">
            {[['username','OPERATOR ID','text'],['email','EMAIL ADDRESS','email'],['password','ACCESS KEY','password'],['full_name','FULL NAME (OPTIONAL)','text']].map(([k, label, type]) => (
              <div key={k} className="auth-field">
                <label className="auth-label">{label}</label>
                <input className="auth-input" type={type} placeholder={label}
                  value={form[k]} onChange={e => setForm(f => ({...f, [k]: e.target.value}))} />
              </div>
            ))}
            <button className="btn btn-primary auth-cta" onClick={doRegister} disabled={loading}>
              <UserPlus size={14} /> {loading ? 'REGISTERING...' : 'REGISTER OPERATOR →'}
            </button>

            <div className="auth-footer">
              <span className="auth-footer-item">AUTH_ERR_LOG: 0</span>
              <div className="auth-footer-links">
                <a href="#">Security Policy</a>
                <a href="#">Help</a>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="auth-bottom-bar">
        <div className="auth-bottom-left">
          <span className="auth-bottom-label">NETWORK STATUS</span>
          <span className="auth-bottom-value">SECURE ENCLAVE ACTIVE</span>
        </div>
        <div className="auth-bottom-right">
          <span className="auth-bottom-label">LAST SIGNAL</span>
          <span className="auth-bottom-value">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  )
}
