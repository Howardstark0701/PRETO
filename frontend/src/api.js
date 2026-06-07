// PRETO API client — all 34 endpoints

const BASE = '/api'

async function req(path, options = {}) {
  const token = localStorage.getItem('preto_token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

const get  = (path, params) => {
  const qs = params ? '?' + new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v != null && v !== ''))
  ).toString() : ''
  return req(`${path}${qs}`)
}
const post   = (path, body) => req(path, { method: 'POST',   body: JSON.stringify(body) })
const put    = (path, body) => req(path, { method: 'PUT',    body: JSON.stringify(body) })
const del    = (path)       => req(path, { method: 'DELETE' })

// ── Repositories ──────────────────────────────────────────────────────────
export const repos = {
  userRepos:       (username, params)    => get(`/repos/user/${username}`, params),
  userStats:       (username)            => get(`/repos/user/${username}/stats`),
  search:          (params)              => get('/repos/search', params),
  searchAdvanced:  (params)              => get('/repos/search/advanced', params),
  repoDetails:     (owner, name)         => get(`/repos/${owner}/${name}`),
  contributors:    (owner, name, n)      => get(`/repos/${owner}/${name}/contributors`, { per_page: n || 10 }),
}

// ── Cache ──────────────────────────────────────────────────────────────────
export const cache = {
  stats:  ()           => get('/cache/stats'),
  clear:  (cacheType)  => del(`/cache/clear${cacheType ? `?cache_type=${cacheType}` : ''}`),
}

// ── Sync ───────────────────────────────────────────────────────────────────
export const sync = {
  syncUser: (username) => post(`/sync/user/${username}`),
  stats:    ()         => get('/sync/stats'),
}

// ── Scheduler ──────────────────────────────────────────────────────────────
export const scheduler = {
  stats:      ()       => get('/scheduler/stats'),
  toggleJob:  (jobId)  => post(`/scheduler/jobs/${jobId}/toggle`),
}

// ── Auth ───────────────────────────────────────────────────────────────────
export const auth = {
  register:    (data)   => post('/auth/register', data),
  login:       (data)   => post('/auth/login', data),
  refresh:     (data)   => post('/auth/refresh', data),
  me:          ()       => get('/auth/me'),
  verifyAuth:  ()       => get('/auth/verify-auth'),
  rateLimit:   ()       => get('/auth/rate_limit'),
  publicProfile: (u)    => get(`/auth/users/${u}`),
  // GitHub OAuth
  githubStatus: ()      => get('/auth/github/status'),
  githubLogin:  ()      => { window.location.href = 'http://localhost:8000/api/auth/github' },
}

// ── Saved Searches ─────────────────────────────────────────────────────────
export const savedSearches = {
  list:    ()          => get('/auth/saved-searches'),
  create:  (data)      => post('/auth/saved-searches', data),
  get:     (id)        => get(`/auth/saved-searches/${id}`),
  update:  (id, data)  => put(`/auth/saved-searches/${id}`, data),
  delete:  (id)        => del(`/auth/saved-searches/${id}`),
  favorite:(id)        => post(`/auth/saved-searches/${id}/favorite`),
}

// ── Search History ─────────────────────────────────────────────────────────
export const history = {
  list:  (limit) => get('/auth/search-history', { limit }),
  clear: ()      => del('/auth/search-history'),
}

// ── API Keys ───────────────────────────────────────────────────────────────
export const apiKeys = {
  list:   ()                                    => get('/auth/api-keys'),
  create: (name, rateLimit, daysUntilExpiry)    => post('/auth/api-keys', null, { name, rate_limit: rateLimit, days_until_expiry: daysUntilExpiry }),
  delete: (id)                                  => del(`/auth/api-keys/${id}`),
  toggle: (id)                                  => post(`/auth/api-keys/${id}/toggle`),
}

// ── Insights (NIM AI) ──────────────────────────────────────────────────────
export const insights = {
  health:        ()       => get('/insights/health'),
  models:        ()       => get('/insights/models'),
  analyze:       (data)   => post('/insights/analyze', data),
  query:         (data)   => post('/insights/query', data),
  searchInsights:(data)   => post('/insights/search-insights', data),
  userAnalysis:  (data)   => post('/insights/user-analysis', data),
}

// ── Advanced ───────────────────────────────────────────────────────────────
export const advanced = {
  export:          (data)  => post('/advanced/export', data),
  exportPdf:       (repos) => fetch('/api/advanced/export?format=pdf', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', ...(localStorage.getItem('preto_token') ? { Authorization: `Bearer ${localStorage.getItem('preto_token')}` } : {}) },
                      body: JSON.stringify(repos)
                    }).then(r => r.blob()),
  analytics:       (data)  => post('/advanced/analytics', data),
  recommendations: (data)  => post('/advanced/recommendations', data),
  report:          (data)  => post('/advanced/report', data),
  compare:         (data)  => post('/advanced/compare', data),
  searchTrends:    (limit) => get('/advanced/search-trends', { limit }),
}

// ── Sources (MACH1 — GitLab, Reddit, HN, X, Dev.to) ────────
export const sources = {
  gitlab: {
    userProjects: (username, perPage) => get(`/sources/gitlab/users/${username}/projects`, { per_page: perPage }),
    search:        (query, perPage)   => get('/sources/gitlab/search', { query, per_page: perPage }),
  },
  reddit: {
    user:        (username)      => get(`/sources/reddit/users/${username}`),
    submissions: (username, lim) => get(`/sources/reddit/users/${username}/submissions`, { limit: lim }),
  },
  hackernews: {
    user:        (username)      => get(`/sources/hackernews/users/${username}`),
    submissions: (username, lim) => get(`/sources/hackernews/users/${username}/submissions`, { limit: lim }),
  },
  x: {
    user:   (username)             => get(`/sources/x/users/${username}`),
    tweets: (username, maxRes)     => get(`/sources/x/users/${username}/tweets`, { max_results: maxRes }),
  },
  devto: {
    user:     (username)          => get(`/sources/devto/users/${username}`),
    articles: (username, perPage) => get(`/sources/devto/users/${username}/articles`, { per_page: perPage }),
  },
}

// ── Misc ────────────────────────────────────────────────────────────────────
export const misc = {
  health:    () => get('/health'),
  metrics:   () => fetch('/api/metrics').then(r => r.text()),
}
