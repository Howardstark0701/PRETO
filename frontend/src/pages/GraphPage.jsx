import { useState, useEffect, useRef, useCallback } from 'react'
import { GitBranch, RefreshCw, Users, Filter, X } from 'lucide-react'
import { repos } from '../api'

/* ── D3 lazy loader ──────────────────────────────────────────────────────── */
let d3Promise = null
function loadD3() {
  if (d3Promise) return d3Promise
  d3Promise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://d3js.org/d3.v7.min.js'
    script.onload  = () => resolve(window.d3)
    script.onerror = reject
    document.head.appendChild(script)
  })
  return d3Promise
}

/* ── Colours ─────────────────────────────────────────────────────────────── */
const NODE_COLORS = {
  user:        '#00d4b4',
  repo:        '#3b82f6',
  lang:        '#f59e0b',
  contributor: '#8b5cf6',
}
const LEGEND = [
  { type: 'user',        label: 'GitHub User'    },
  { type: 'repo',        label: 'Repository'     },
  { type: 'lang',        label: 'Language'       },
  { type: 'contributor', label: 'Contributor'    },
]

/* ── Graph builder ───────────────────────────────────────────────────────── */
function buildGraph(username, reposData, contributorMap = {}, filters = {}) {
  const nodes = []
  const links = []
  const seen  = new Set()

  const addNode = (id, type, label, meta = {}) => {
    if (!seen.has(id)) { seen.add(id); nodes.push({ id, type, label, ...meta }) }
  }

  addNode(username, 'user', username, { url: `https://github.com/${username}` })

  reposData.forEach(r => {
    // Apply star filter
    if (filters.minStars && r.stargazers_count < filters.minStars) return
    // Apply language filter
    if (filters.language && r.language !== filters.language) return

    const rid = r.full_name || r.name
    addNode(rid, 'repo', r.name, {
      stars: r.stargazers_count || 0,
      forks: r.forks_count || 0,
      url:   r.html_url,
      desc:  r.description,
      lang:  r.language,
    })
    links.push({ source: username, target: rid, type: 'owns' })

    if (r.language) {
      const lid = `lang:${r.language}`
      addNode(lid, 'lang', r.language)
      links.push({ source: rid, target: lid, type: 'uses' })
    }

    // Contributor nodes
    const contribs = contributorMap[rid] || []
    contribs.forEach(c => {
      const cid = `contrib:${c.login}`
      addNode(cid, 'contributor', c.login, {
        url:          c.html_url,
        avatar:       c.avatar_url,
        contributions: c.contributions,
      })
      links.push({ source: rid, target: cid, type: 'contributed' })
    })
  })

  return { nodes, links }
}

/* ── D3 render ───────────────────────────────────────────────────────────── */
function renderGraph(svgEl, { nodes, links }, onSelect) {
  const d3     = window.d3
  const width  = svgEl.clientWidth  || 900
  const height = svgEl.clientHeight || 580

  d3.select(svgEl).selectAll('*').remove()

  const svg = d3.select(svgEl).attr('width', width).attr('height', height)
  const g   = svg.append('g')

  svg.call(
    d3.zoom().scaleExtent([0.15, 5])
      .on('zoom', e => g.attr('transform', e.transform))
  )

  // Arrow markers
  const defs = svg.append('defs')
  const markerDefs = {
    owns:        '#00d4b4',
    uses:        '#475569',
    contributed: '#8b5cf6',
  }
  Object.entries(markerDefs).forEach(([id, color]) => {
    defs.append('marker')
      .attr('id', `arrow-${id}`)
      .attr('viewBox', '0 -4 8 8').attr('refX', 20).attr('refY', 0)
      .attr('markerWidth', 5).attr('markerHeight', 5).attr('orient', 'auto')
      .append('path').attr('d', 'M0,-4L8,0L0,4').attr('fill', color)
  })

  const linkColor = { owns: 'rgba(0,212,180,0.25)', uses: 'rgba(71,85,105,0.4)', contributed: 'rgba(139,92,246,0.3)' }

  const sim = d3.forceSimulation(nodes)
    .force('link',      d3.forceLink(links).id(d => d.id).distance(d => ({ owns: 120, uses: 70, contributed: 80 }[d.type] || 80)).strength(0.6))
    .force('charge',    d3.forceManyBody().strength(-260))
    .force('center',    d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(26))

  const link = g.append('g').selectAll('line').data(links).join('line')
    .attr('stroke',       d => linkColor[d.type] || 'rgba(100,116,139,0.3)')
    .attr('stroke-width', d => d.type === 'owns' ? 1.5 : 1)
    .attr('marker-end',   d => `url(#arrow-${d.type})`)

  const node = g.append('g').selectAll('g').data(nodes).join('g')
    .attr('cursor', 'pointer')
    .call(
      d3.drag()
        .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
        .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y })
        .on('end',   (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null })
    )
    .on('click', (e, d) => { e.stopPropagation(); onSelect(d) })

  const radius = d => ({ user: 20, repo: 12, lang: 8, contributor: 9 }[d.type] || 10)

  node.append('circle')
    .attr('r',              radius)
    .attr('fill',           d => NODE_COLORS[d.type] || '#64748b')
    .attr('fill-opacity',   0.8)
    .attr('stroke',         d => NODE_COLORS[d.type] || '#64748b')
    .attr('stroke-width',   d => d.type === 'user' ? 3 : 1.5)
    .attr('stroke-opacity', 0.5)

  node.append('text')
    .attr('dy',           d => radius(d) + 12)
    .attr('text-anchor',  'middle')
    .attr('fill',         '#94a3b8')
    .attr('font-size',    d => d.type === 'user' ? 11 : 8.5)
    .attr('font-family',  'JetBrains Mono, monospace')
    .text(d => d.label.length > 16 ? d.label.slice(0, 14) + '…' : d.label)

  // Star badges
  node.filter(d => d.type === 'repo' && d.stars > 0)
    .append('text')
    .attr('dy', -radius(null) - 2).attr('text-anchor', 'middle')
    .attr('fill', '#f59e0b').attr('font-size', 7.5)
    .text(d => `★${d.stars >= 1000 ? (d.stars/1000).toFixed(1)+'k' : d.stars}`)

  // Contribution count badge
  node.filter(d => d.type === 'contributor')
    .append('text')
    .attr('dy', -11).attr('text-anchor', 'middle')
    .attr('fill', '#8b5cf6').attr('font-size', 7)
    .text(d => d.contributions ? `+${d.contributions}` : '')

  sim.on('tick', () => {
    link
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    node.attr('transform', d => `translate(${d.x},${d.y})`)
  })

  return sim
}

/* ── Main component ──────────────────────────────────────────────────────── */
export default function GraphPage() {
  const [username, setUsername]         = useState('')
  const [loading, setLoading]           = useState(false)
  const [contribLoading, setContribLoading] = useState(false)
  const [error, setError]               = useState(null)
  const [graphData, setGraphData]       = useState(null)   // { nodes, links } raw
  const [reposCache, setReposCache]     = useState([])
  const [contribMap, setContribMap]     = useState({})
  const [selected, setSelected]         = useState(null)
  const [showContribs, setShowContribs] = useState(false)
  const [filterLang, setFilterLang]     = useState('')
  const [filterStars, setFilterStars]   = useState('')
  const [stats, setStats]               = useState(null)
  const svgRef = useRef(null)
  const simRef = useRef(null)

  // Rebuild and re-render when filters or contributor data changes
  useEffect(() => {
    if (!reposCache.length) return
    const filters = {
      language:  filterLang  || null,
      minStars:  filterStars ? parseInt(filterStars) : 0,
    }
    const graph = buildGraph(username, reposCache, showContribs ? contribMap : {}, filters)
    setStats({ nodeCount: graph.nodes.length, linkCount: graph.links.length })
    requestAnimationFrame(() => {
      if (simRef.current) simRef.current.stop()
      simRef.current = renderGraph(svgRef.current, graph, setSelected)
    })
  }, [reposCache, contribMap, showContribs, filterLang, filterStars])

  async function loadGraph() {
    if (!username.trim()) return
    setLoading(true); setError(null); setSelected(null)
    setContribMap({}); setShowContribs(false)
    try {
      await loadD3()
      const data = await repos.userRepos(username, { per_page: 50, sort_by: 'stars' })
      setReposCache(data.repos || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function loadContributors() {
    if (!reposCache.length) return
    setContribLoading(true)
    const map = {}
    // Load contributors for top 8 repos only (rate limit friendly)
    const topRepos = reposCache.slice(0, 8)
    await Promise.allSettled(
      topRepos.map(async r => {
        try {
          const owner = r.full_name?.split('/')[0] || username
          const data  = await repos.contributors(owner, r.name, 5)
          map[r.full_name || r.name] = data.contributors || []
        } catch { /* skip failed repos */ }
      })
    )
    setContribMap(map)
    setShowContribs(true)
    setContribLoading(false)
  }

  function reheat() {
    if (simRef.current) simRef.current.alpha(0.5).restart()
  }

  function clearFilters() {
    setFilterLang(''); setFilterStars('')
  }

  // Unique languages for filter dropdown
  const languages = [...new Set(reposCache.map(r => r.language).filter(Boolean))].sort()

  return (
    <div className="page" style={{ paddingBottom: 0, display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div className="page-header">
        <div className="page-title">GRAPH ANALYSIS</div>
        <div className="page-sub">Force-directed repository · language · contributor network</div>
      </div>

      {/* Controls */}
      <div className="panel" style={{ marginBottom: 10, flexShrink: 0 }}>
        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">GitHub Username</label>
            <input className="form-input" placeholder="torvalds"
              value={username} onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadGraph()} />
          </div>
          <button className="btn btn-primary" onClick={loadGraph} disabled={loading}>
            <GitBranch size={13} /> {loading ? 'Building...' : 'Build Graph'}
          </button>
          {reposCache.length > 0 && (
            <>
              <button className="btn btn-secondary" onClick={loadContributors} disabled={contribLoading}
                title="Expand with contributor nodes (top 8 repos, 5 contributors each)">
                <Users size={13} /> {contribLoading ? 'Loading...' : showContribs ? 'Refresh Contribs' : 'Add Contributors'}
              </button>
              {showContribs && (
                <button className="btn btn-secondary" onClick={() => setShowContribs(false)} title="Hide contributors">
                  <X size={13} /> Contributors
                </button>
              )}
              <button className="btn btn-secondary" onClick={reheat} title="Reheat simulation">
                <RefreshCw size={13} />
              </button>
            </>
          )}
        </div>

        {/* Filters */}
        {reposCache.length > 0 && (
          <div className="form-row" style={{ marginTop: 8 }}>
            <Filter size={12} style={{ color: 'var(--text-muted)', marginTop: 8 }} />
            <div className="form-group">
              <label className="form-label">Language</label>
              <select className="form-select" style={{ minWidth: 120 }}
                value={filterLang} onChange={e => setFilterLang(e.target.value)}>
                <option value="">All</option>
                {languages.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Min Stars</label>
              <input className="form-input" style={{ minWidth: 80 }} type="number"
                placeholder="0" value={filterStars} onChange={e => setFilterStars(e.target.value)} />
            </div>
            {(filterLang || filterStars) && (
              <button className="btn btn-secondary" onClick={clearFilters} style={{ marginTop: 16 }}>
                <X size={12} /> Clear
              </button>
            )}
          </div>
        )}
      </div>

      {error && <div className="error-box" style={{ marginBottom: 8 }}>{error}</div>}

      {/* Legend + stats */}
      {stats && (
        <div style={{ display: 'flex', gap: 14, marginBottom: 6, flexShrink: 0, flexWrap: 'wrap', alignItems: 'center' }}>
          {LEGEND.filter(l => l.type !== 'contributor' || showContribs).map(({ type, label }) => (
            <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, color: 'var(--text-muted)' }}>
              <span style={{ width: 9, height: 9, borderRadius: '50%', background: NODE_COLORS[type], display: 'inline-block' }} />
              {label}
            </div>
          ))}
          <span style={{ fontSize: 10, color: 'var(--text-muted)', marginLeft: 'auto' }}>
            {stats.nodeCount} nodes · {stats.linkCount} edges
            {(filterLang || filterStars) && <span style={{ color: 'var(--warn)', marginLeft: 6 }}>FILTERED</span>}
          </span>
        </div>
      )}

      {/* SVG canvas */}
      <div style={{
        flex: 1, background: 'var(--bg-panel)', border: '1px solid var(--border)',
        borderRadius: 6, overflow: 'hidden', position: 'relative', minHeight: 380,
      }}>
        <svg ref={svgRef} style={{ width: '100%', height: '100%', display: 'block' }} />

        {!reposCache.length && !loading && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 12, gap: 8,
          }}>
            <GitBranch size={38} style={{ opacity: 0.2 }} />
            <div>Enter a GitHub username to build the graph</div>
            <div style={{ fontSize: 10, opacity: 0.5 }}>Drag · Scroll to zoom · Click for details · Filter by language/stars</div>
          </div>
        )}

        {(loading || contribLoading) && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex', alignItems: 'center',
            justifyContent: 'center', background: 'rgba(11,14,20,0.7)',
          }}>
            <div className="loading">
              <div className="spinner" />
              {loading ? 'Loading repository data...' : 'Fetching contributors...'}
            </div>
          </div>
        )}
      </div>

      {/* Node detail panel */}
      {selected && (
        <div style={{
          position: 'fixed', right: 16, bottom: 16,
          background: 'var(--bg-panel)',
          border: `1px solid ${NODE_COLORS[selected.type] || 'var(--border)'}`,
          borderRadius: 8, padding: 16, minWidth: 240, maxWidth: 300,
          zIndex: 100, boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span className={`badge ${selected.type === 'user' ? 'badge-green' : selected.type === 'repo' ? 'badge-blue' : selected.type === 'contributor' ? 'badge-yellow' : 'badge-yellow'}`}>
              {selected.type.toUpperCase()}
            </span>
            <button style={{ background:'none', border:'none', color:'var(--text-muted)', cursor:'pointer', fontSize:16 }}
              onClick={() => setSelected(null)}>×</button>
          </div>

          {selected.avatar && (
            <img src={selected.avatar} alt="" style={{ width: 32, height: 32, borderRadius:'50%', marginBottom: 8, border: '2px solid var(--accent)' }} />
          )}

          <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4, color: 'var(--text-primary)', wordBreak: 'break-word' }}>
            {selected.label}
          </div>

          {selected.desc && (
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8, lineHeight: 1.4 }}>{selected.desc}</div>
          )}
          {selected.type === 'repo' && (
            <div style={{ display:'flex', gap:10, fontSize:11, color:'var(--text-dim)', marginBottom:8 }}>
              <span>★ {(selected.stars||0).toLocaleString()}</span>
              <span>⑂ {(selected.forks||0).toLocaleString()}</span>
              {selected.lang && <span className="tag">{selected.lang}</span>}
            </div>
          )}
          {selected.type === 'contributor' && selected.contributions && (
            <div style={{ fontSize:11, color:'var(--text-dim)', marginBottom:8 }}>
              {selected.contributions} commits
            </div>
          )}
          {selected.url && (
            <a href={selected.url} target="_blank" rel="noreferrer" style={{ fontSize:11, color:'var(--accent)' }}>
              Open on GitHub →
            </a>
          )}
        </div>
      )}
    </div>
  )
}
