import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Shield, LogIn, UserPlus, Key, LogOut, History, Bookmark, Github } from 'lucide-react'
import { auth, savedSearches, history, apiKeys } from '../api'

// ── OAuth callback handler (reads tokens from URL hash) ──────────────────
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
      // Fetch full profile
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

  useGithubCallback(setToken, setUser)

  useEffect(() => {
    if (token) {
      auth.me().then(setUser).catch(() => {
        localStorage.removeItem('preto_token')
        setToken(null)
      })
    }
    // Check GitHub OAuth config
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
      setMsg('Logged in successfully')
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function doRegister() {
    setLoading(true); setError(null)
    try {
      await auth.register(form)
      setMsg('Registered! You can now log in.'); setTab('login')
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  function doLogout() {
    localStorage.removeItem('preto_token')
    localStorage.removeItem('preto_refresh')
    setToken(null); setUser(null)
    setSaves(null); setHist(null); setKeys(null)
    setMsg('Logged out')
  }

  async function loadSaves() { try { const d = await savedSearches.list(); setSaves(d.searches) } catch(e) { setError(e.message) } }
  async function loadHist()  { try { const d = await history.list(20); setHist(d.history) }      catch(e) { setError(e.message) } }
  async function loadKeys()  { try { const d = await apiKeys.list(); setKeys(d.keys) }            catch(e) { setError(e.message) } }
  async function clearHist() { try { await history.clear(); setHist([]); setMsg('History cleared') } catch(e) { setError(e.message) } }

  async function createKey() {
    const name = window.prompt('API key name:'); if (!name) return
    try {
      const data = await apiKeys.create(name, 100)
      alert(`Your new API key (save it now — shown ONCE):\n\n${data.raw_key}`)
      loadKeys()
    } catch(e) { setError(e.message) }
  }

  // ── Authenticated view ────────────────────────────────────────────────
  if (token && user) return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">AUTH & ACCOUNT</div>
        <div className="page-sub">Manage your PRETO account</div>
      </div>

      <div className="panel" style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
        {user.avatar_url
          ? <img src={user.avatar_url} alt="" style={{ width: 36, height: 36, borderRadius: '50%', border: '2px solid var(--accent)' }} />
          : <Shield size={20} style={{ color: 'var(--accent)' }} />
        }
        <div>
          <div style={{ fontWeight: 700 }}>{user.username}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{user.email}</div>
          {user.github_login && (
            <div style={{ fontSize: 10, color: 'var(--accent)', marginTop: 2 }}>
              <Github size={10} style={{ display: 'inline', marginRight: 3 }} />
              github.com/{user.github_login}
            </div>
          )}
        </div>
        <span className="badge badge-green">AUTHENTICATED</span>
        {user.github_login && <span className="badge badge-blue">GITHUB OAUTH</span>}
        <button className="btn btn-danger" style={{ marginLeft: 'auto' }} onClick={doLogout}>
          <LogOut size={13} /> Logout
        </button>
      </div>

      {msg   && <div style={{ padding: '8px 12px', background: 'rgba(0,212,180,0.1)', borderRadius: 4, fontSize: 12, color: 'var(--accent)', marginBottom: 12 }}>{msg}</div>}
      {error && <div className="error-box" style={{ marginBottom: 12 }}>{error}</div>}

      <div className="tabs">
        {[['saves','Saved Searches'],['hist','Search History'],['keys','API Keys']].map(([k,l]) => (
          <button key={k} className={`tab ${tab===k?'active':''}`}
            onClick={() => {
              setTab(k)
              if (k==='saves') loadSaves()
              if (k==='hist') loadHist()
              if (k==='keys') loadKeys()
            }}>{l}</button>
        ))}
      </div>

      {tab === 'saves' && (
        <div className="panel">
          <div className="panel-title"><Bookmark size={11} style={{ display:'inline', marginRight:5 }}/>SAVED SEARCHES</div>
          {saves === null && <button className="btn btn-secondary" onClick={loadSaves}>Load</button>}
          {saves?.length === 0 && <div className="empty-state">No saved searches yet</div>}
          {saves?.length > 0 && (
            <table className="data-table">
              <thead><tr><th>Query</th><th>Language</th><th>Fav</th><th>Saved</th><th></th></tr></thead>
              <tbody>{saves.map(s => (
                <tr key={s.id}>
                  <td style={{ color: 'var(--accent)' }}>{s.query}</td>
                  <td>{s.language || '—'}</td>
                  <td>{s.is_favorite ? '★' : '☆'}</td>
                  <td style={{ fontSize: 10 }}>{new Date(s.created_at).toLocaleDateString()}</td>
                  <td style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-secondary" style={{ fontSize: 10, padding: '2px 6px' }}
                      onClick={async () => { await savedSearches.favorite(s.id); loadSaves() }}>★</button>
                    <button className="btn btn-danger" style={{ fontSize: 10, padding: '2px 6px' }}
                      onClick={async () => { await savedSearches.delete(s.id); loadSaves() }}>Del</button>
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
            <div className="panel-title"><History size={11} style={{ display:'inline', marginRight:5 }}/>SEARCH HISTORY</div>
            <button className="btn btn-danger" style={{ fontSize: 10 }} onClick={clearHist}>Clear All</button>
          </div>
          {hist === null && <button className="btn btn-secondary" onClick={loadHist}>Load</button>}
          {hist?.length === 0 && <div className="empty-state">No history yet</div>}
          {hist?.length > 0 && (
            <table className="data-table">
              <thead><tr><th>Query</th><th>Results</th><th>Cache</th><th>Time</th></tr></thead>
              <tbody>{hist.map((h, i) => (
                <tr key={i}>
                  <td>{h.query}</td>
                  <td>{h.results_count}</td>
                  <td><span className={`badge ${h.used_cache ? 'badge-green' : 'badge-yellow'}`}>{h.used_cache ? 'HIT' : 'MISS'}</span></td>
                  <td style={{ fontSize: 10 }}>{new Date(h.created_at).toLocaleString()}</td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}

      {tab === 'keys' && (
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
            <div className="panel-title"><Key size={11} style={{ display:'inline', marginRight:5 }}/>API KEYS</div>
            <button className="btn btn-primary" style={{ fontSize: 10 }} onClick={createKey}>+ New Key</button>
          </div>
          {keys === null && <button className="btn btn-secondary" onClick={loadKeys}>Load</button>}
          {keys?.length === 0 && <div className="empty-state">No API keys yet</div>}
          {keys?.length > 0 && (
            <table className="data-table">
              <thead><tr><th>Name</th><th>Prefix</th><th>Rate</th><th>Status</th><th>Last Used</th><th></th></tr></thead>
              <tbody>{keys.map(k => (
                <tr key={k.id}>
                  <td>{k.name}</td>
                  <td style={{ fontFamily: 'monospace', color: 'var(--accent)', fontSize: 11 }}>{k.prefix}...</td>
                  <td>{k.rate_limit}/min</td>
                  <td><span className={`badge ${k.is_active ? 'badge-green' : 'badge-red'}`}>{k.is_active ? 'ACTIVE' : 'OFF'}</span></td>
                  <td style={{ fontSize: 10 }}>{k.last_used ? new Date(k.last_used).toLocaleDateString() : 'Never'}</td>
                  <td style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-secondary" style={{ fontSize: 10, padding: '2px 6px' }}
                      onClick={async () => { await apiKeys.toggle(k.id); loadKeys() }}>Toggle</button>
                    <button className="btn btn-danger" style={{ fontSize: 10, padding: '2px 6px' }}
                      onClick={async () => { await apiKeys.delete(k.id); loadKeys() }}>Del</button>
                  </td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </div>
      )}
    </div>
  )

  // ── Login / Register view ─────────────────────────────────────────────
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">AUTH & ACCOUNT</div>
        <div className="page-sub">Login or register to unlock saved searches and API keys</div>
      </div>

      {/* GitHub OAuth button */}
      <div className="panel" style={{ marginBottom: 16, maxWidth: 360 }}>
        <div className="panel-title"><Github size={11} style={{ display:'inline', marginRight:5 }}/>GITHUB LOGIN</div>
        <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12, lineHeight: 1.6 }}>
          Login with GitHub to get <span style={{ color: 'var(--accent)' }}>5000 req/hr</span> rate limit
          instead of 60. No password needed.
        </p>
        {ghStatus && !ghStatus.configured && (
          <div style={{ fontSize: 10, color: 'var(--warn)', marginBottom: 10, lineHeight: 1.5 }}>
            ⚠ OAuth not configured. Add GITHUB_CLIENT_ID + GITHUB_CLIENT_SECRET to .env
            <br />Create at: github.com/settings/developers
          </div>
        )}
        <button
          className="btn"
          style={{ background: '#24292e', color: '#fff', border: '1px solid #444', width: '100%', justifyContent: 'center', fontSize: 13 }}
          onClick={() => auth.githubLogin()}
          disabled={ghStatus && !ghStatus.configured}
        >
          <Github size={15} />
          Continue with GitHub
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, maxWidth: 360, marginBottom: 16 }}>
        <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--border)' }} />
        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>OR</span>
        <hr style={{ flex: 1, border: 'none', borderTop: '1px solid var(--border)' }} />
      </div>

      <div className="tabs" style={{ maxWidth: 360 }}>
        {[['login','Login'],['register','Register']].map(([k,l]) => (
          <button key={k} className={`tab ${tab===k?'active':''}`} onClick={() => { setTab(k); setError(null); setMsg(null) }}>{l}</button>
        ))}
      </div>

      {error && <div className="error-box" style={{ marginBottom: 12, maxWidth: 360 }}>{error}</div>}
      {msg   && <div style={{ padding: '8px 12px', background: 'rgba(0,212,180,0.1)', borderRadius: 4, fontSize: 12, color: 'var(--accent)', marginBottom: 12, maxWidth: 360 }}>{msg}</div>}

      {tab === 'login' && (
        <div className="panel" style={{ maxWidth: 360 }}>
          <div className="panel-title"><LogIn size={11} style={{ display:'inline', marginRight:5 }}/>LOGIN</div>
          <div className="form-group" style={{ marginBottom: 10 }}>
            <label className="form-label">Username or Email</label>
            <input className="form-input" style={{ width: '100%', minWidth: 'unset' }} {...field('username')}
              onKeyDown={e => e.key==='Enter' && doLogin()} />
          </div>
          <div className="form-group" style={{ marginBottom: 14 }}>
            <label className="form-label">Password</label>
            <input className="form-input" style={{ width: '100%', minWidth: 'unset' }} type="password" {...field('password')}
              onKeyDown={e => e.key==='Enter' && doLogin()} />
          </div>
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={doLogin} disabled={loading}>
            <LogIn size={13} /> {loading ? 'Logging in...' : 'Login'}
          </button>
        </div>
      )}

      {tab === 'register' && (
        <div className="panel" style={{ maxWidth: 360 }}>
          <div className="panel-title"><UserPlus size={11} style={{ display:'inline', marginRight:5 }}/>REGISTER</div>
          {[
            ['username', 'Username', 'text'],
            ['email', 'Email', 'email'],
            ['password', 'Password', 'password'],
            ['full_name', 'Full Name (optional)', 'text']
          ].map(([k, label, type]) => (
            <div key={k} className="form-group" style={{ marginBottom: 10 }}>
              <label className="form-label">{label}</label>
              <input className="form-input" style={{ width: '100%', minWidth: 'unset' }} type={type} {...field(k)} />
            </div>
          ))}
          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={doRegister} disabled={loading}>
            <UserPlus size={13} /> {loading ? 'Registering...' : 'Register'}
          </button>
        </div>
      )}
    </div>
  )
}
