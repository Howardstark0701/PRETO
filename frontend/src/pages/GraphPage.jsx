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
    if (filters.minStars && r.stargazers_count < filters.minStars) return
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

    const contribs = contributorMap[rid] || []
    contribs.forEach(c => {
      const cid = `contrib:${c.login}`
      addNode(cid, 'contributor', c.login, {
        url: c.html_url, avatar: c.avatar_url, contributions: c.contributions,
      })
      links.push({ source: rid, target: cid, type: 'contributed' })
    })
  })

  return { nodes, links }
}

/* ── D3 render ───────────────────────────────────────────────────────────── */
function renderGraph(svgEl, { nodes, links }, onSelect) {
  const d3     = window.d3
  const rect  = svgEl.getBoundingClientRect()
  const width  = rect.width  || 900
  const height = rect.height || 580

  d3.select(svgEl).selectAll('*').remove()

  const svg = d3.select(svgEl)
    .attr('width', width).attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`)
  const g   = svg.append('g')

  svg.call(
    d3.zoom().scaleExtent([0.15, 5])
      .on('zoom', e => g.attr('transform', e.transform))
  )

  // Edge glow filter
  const defs = svg.append('defs')
  defs.append('filter').attr('id', 'edge-glow').attr('x', '-20%').attr('y', '-20%').attr('width', '140%').attr('height', '140%')
    .append('feGaussianBlur').attr('stdDeviation', 2).attr('result', 'blur')
  const merge = defs.select('#edge-glow').append('feMerge')
  merge.append('feMergeNode').attr('in', 'blur')
  merge.append('feMergeNode').attr('in', 'SourceGraphic')

  // Arrow markers
  const markerDefs = { owns: '#00d4b4', uses: '#475569', contributed: '#8b5cf6' }
  Object.entries(markerDefs).forEach(([id, color]) => {
    defs.append('marker')
      .attr('id', `arrow-${id}`)
      .attr('viewBox', '0 -4 8 8').attr('refX', 20).attr('refY', 0)
      .attr('markerWidth', 5).attr('markerHeight', 5).attr('orient', 'auto')
      .append('path').attr('d', 'M0,-4L8,0L0,4').attr('fill', color)
  })

  const linkColor = { owns: 'rgba(0,212,180,0.25)', uses: 'rgba(71,85,105,0.4)', contributed: 'rgba(139,92,246,0.3)' }
  const linkGlowColor = { owns: 'rgba(0,212,180,0.15)', uses: 'transparent', contributed: 'rgba(139,92,246,0.15)' }

  const sim = d3.forceSimulation(nodes)
    .force('link',      d3.forceLink(links).id(d => d.id).distance(d => ({ owns: 160, uses: 90, contributed: 100 }[d.type] || 100)).strength(0.5))
    .force('charge',    d3.forceManyBody().strength(-360))
    .force('center',    d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide(34))

  // Glow edges (behind regular edges)
  const glowLink = g.append('g').selectAll('line').data(links).join('line')
    .attr('stroke',       d => linkGlowColor[d.type] || 'transparent')
    .attr('stroke-width', d => d.type === 'owns' ? 6 : 3)
    .attr('filter',       d => d.type === 'owns' ? 'url(#edge-glow)' : null)
    .attr('marker-end',   d => `url(#arrow-${d.type})`)

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

  // Node glow
  node.append('circle')
    .attr('r',              d => radius(d) + 3)
    .attr('fill',           d => NODE_COLORS[d.type] || '#64748b')
    .attr('fill-opacity',   0.1)
    .attr('stroke',         'none')

  node.append('circle')
    .attr('r',              radius)
    .attr('fill',           d => NODE_COLORS[d.type] || '#64748b')
    .attr('fill-opacity',   0.8)
    .attr('stroke',         d => NODE_COLORS[d.type] || '#64748b')
    .attr('stroke-width',   d => d.type === 'user' ? 3 : 1.5)
    .attr('stroke-opacity', 0.5)

  node.append('text')
    .attr('dy',           d => radius(d) + 14)
    .attr('text-anchor',  'middle')
    .attr('fill',         '#94a3b8')
    .attr('font-size',    d => d.type === 'user' ? 11 : 9)
    .attr('font-family',  'JetBrains Mono, monospace')
    .attr('clip-path',    (d, i) => `url(#clip-${i})`)
    .text(d => d.label.length > 18 ? d.label.slice(0, 16) + '…' : d.label)

  // stagger labels for lang + contributor nodes to reduce overlap
  node.filter(d => d.type === 'lang' || d.type === 'contributor')
    .select('text')
    .attr('dy', (d, i) => radius(d) + (i % 2 === 0 ? 14 : 22))

  node.filter(d => d.type === 'repo' && d.stars > 0)
    .append('text')
    .attr('dy', -radius(null) - 2).attr('text-anchor', 'middle')
    .attr('fill', '#f59e0b').attr('font-size', 7.5)
    .text(d => `★${d.stars >= 1000 ? (d.stars/1000).toFixed(1)+'k' : d.stars}`)

  node.filter(d => d.type === 'contributor')
    .append('text')
    .attr('dy', -11).attr('text-anchor', 'middle')
    .attr('fill', '#8b5cf6').attr('font-size', 7)
    .text(d => d.contributions ? `+${d.contributions}` : '')

  sim.on('tick', () => {
    link
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y)
    glowLink
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
  const [graphData, setGraphData]       = useState(null)
  const [reposCache, setReposCache]     = useState([])
  const [contribMap, setContribMap]     = useState({})
  const [selected, setSelected]         = useState(null)
  const [showContribs, setShowContribs] = useState(false)
  const [filterLang, setFilterLang]     = useState('')
  const [filterStars, setFilterStars]   = useState('')
  const [stats, setStats]               = useState(null)
  const svgRef = useRef(null)
  const simRef = useRef(null)

  useEffect(() => {
    if (!reposCache.length) return
    const filters = { language: filterLang || null, minStars: filterStars ? parseInt(filterStars) : 0 }
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
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function loadContributors() {
    if (!reposCache.length) return
    setContribLoading(true)
    const map = {}
    const topRepos = reposCache.slice(0, 8)
    await Promise.allSettled(
      topRepos.map(async r => {
        try {
          const owner = r.full_name?.split('/')[0] || username
          const data  = await repos.contributors(owner, r.name, 5)
          map[r.full_name || r.name] = data.contributors || []
        } catch { /* skip */ }
      })
    )
    setContribMap(map)
    setShowContribs(true)
    setContribLoading(false)
  }

  function reheat() { if (simRef.current) simRef.current.alpha(0.5).restart() }
  function clearFilters() { setFilterLang(''); setFilterStars('') }
  function closeSelected() { setSelected(null) }

  const languages = [...new Set(reposCache.map(r => r.language).filter(Boolean))].sort()

  return (
    <div className="page" style={{ paddingBottom: 0, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 48px)' }}>
      <div className="breadcrumb">OSINT COMMAND / GRAPH_ANALYSIS</div>

      {/* Controls */}
      <div className="panel" style={{ marginBottom: 10, flexShrink: 0 }}>
        <div className="panel-header"><GitBranch size={11} /> NETWORK_GRAPH_CONTROLS</div>
        <div className="form-row">
          <div className="form-group" style={{ flex: 1 }}>
            <label className="form-label">TARGET USERNAME</label>
            <input className="form-input" style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}
              placeholder="torvalds"
              value={username} onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadGraph()} />
          </div>
          <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={loadGraph} disabled={loading}>
            <GitBranch size={12} /> {loading ? '⟳ BUILDING...' : '▼ BUILD GRAPH'}
          </button>
          {reposCache.length > 0 && (
            <>
              <button className="btn btn-secondary" style={{ marginTop: 16 }} onClick={loadContributors} disabled={contribLoading}>
                <Users size={12} /> {contribLoading ? '⟳' : showContribs ? 'REFRESH' : '+ CONTRIBUTORS'}
              </button>
              {showContribs && (
                <button className="btn btn-secondary" style={{ marginTop: 16 }} onClick={() => setShowContribs(false)}>
                  <X size={12} /> HIDE
                </button>
              )}
              <button className="btn btn-secondary" style={{ marginTop: 16 }} onClick={reheat} title="Reheat">
                <RefreshCw size={12} />
              </button>
            </>
          )}
        </div>

        {reposCache.length > 0 && (
          <div className="form-row" style={{ marginTop: 8 }}>
            <Filter size={12} style={{ color: 'var(--text-muted)', marginTop: 16 }} />
            <div className="form-group">
              <label className="form-label">LANGUAGE</label>
              <select className="form-select" style={{ fontSize: 11 }}
                value={filterLang} onChange={e => setFilterLang(e.target.value)}>
                <option value="">ALL</option>
                {languages.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">MIN STARS</label>
              <input className="form-input" style={{ minWidth: 80, fontSize: 11 }} type="number"
                placeholder="0" value={filterStars} onChange={e => setFilterStars(e.target.value)} />
            </div>
            {(filterLang || filterStars) && (
              <button className="btn btn-secondary btn-sm" style={{ marginTop: 16 }} onClick={clearFilters}>
                <X size={11} /> CLEAR
              </button>
            )}
          </div>
        )}
      </div>

      {error && <div className="msg-box msg-error" style={{ marginBottom: 8 }}>{error}</div>}

      {/* Legend + stats */}
      {stats && (
        <div style={{ display: 'flex', gap: 10, marginBottom: 6, flexShrink: 0, flexWrap: 'wrap', alignItems: 'center' }}>
          {[
            { type: 'user', label: 'USER' },
            { type: 'repo', label: 'REPO' },
            { type: 'lang', label: 'LANG' },
            ...(showContribs ? [{ type: 'contributor', label: 'CONTRIB' }] : []),
          ].map(({ type, label }) => (
            <span key={type} className="status-badge" style={{
              fontSize: 8, padding: '1px 6px', color: NODE_COLORS[type],
              borderColor: NODE_COLORS[type] + '80',
            }}>● {label}</span>
          ))}
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-muted)', marginLeft: 'auto' }}>
            {stats.nodeCount} NODES · {stats.linkCount} EDGES
            {(filterLang || filterStars) && <span style={{ color: 'var(--warn)', marginLeft: 6 }}>FILTERED</span>}
          </span>
        </div>
      )}

      {/* Main area: canvas + detail panel */}
      <div style={{ display: 'flex', gap: 10, flex: 1, minHeight: 520 }}>
        {/* SVG canvas */}
        <div style={{
          flex: 1, background: 'var(--bg-panel)', border: '1px solid var(--border)',
          overflow: 'hidden', position: 'relative',
        }}>
          <svg ref={svgRef} style={{ width: '100%', height: '100%', display: 'block' }} />

          {!reposCache.length && !loading && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: 12, gap: 8,
            }}>
              <GitBranch size={38} style={{ opacity: 0.2 }} />
              <div style={{ fontFamily: 'var(--font-mono)', letterSpacing: 1 }}>AWAITING TARGET INPUT</div>
              <div style={{ fontSize: 10, opacity: 0.5 }}>DRAG · ZOOM · CLICK FOR DETAILS</div>
            </div>
          )}

          {(loading || contribLoading) && (
            <div style={{
              position: 'absolute', inset: 0, display: 'flex', alignItems: 'center',
              justifyContent: 'center', background: 'rgba(11,14,20,0.7)',
            }}>
              <div className="loading">
                <div className="spinner" />
                {loading ? 'BUILDING NETWORK GRAPH...' : 'FETCHING CONTRIBUTORS...'}
              </div>
            </div>
          )}
        </div>

        {/* Node Detail Panel (right sidebar) */}
        {selected && (
          <div style={{
            width: 220, minWidth: 220, background: 'var(--bg-panel)', border: '1px solid var(--border)',
            padding: 14, display: 'flex', flexDirection: 'column', overflowY: 'auto',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span className="status-badge" style={{
                fontSize: 8, padding: '1px 6px',
                color: NODE_COLORS[selected.type] || 'var(--text-muted)',
                borderColor: (NODE_COLORS[selected.type] || 'var(--text-muted)') + '80',
              }}>● {selected.type?.toUpperCase()}</span>
              <button className="btn btn-sm btn-secondary" style={{ padding: '2px 6px' }} onClick={closeSelected}>
                <X size={10} />
              </button>
            </div>

            {selected.avatar && (
              <img src={selected.avatar} alt="" style={{
                width: 32, height: 32, marginBottom: 8,
                border: '2px solid var(--accent)', background: 'var(--bg-base)',
              }} />
            )}

            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 700, color: 'var(--accent)', wordBreak: 'break-word', marginBottom: 8 }}>
              {selected.label}
            </div>

            {selected.desc && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4, marginBottom: 8 }}>
                {selected.desc}
              </div>
            )}

            {selected.type === 'repo' && (
              <>
                <div className="meta-row"><span className="meta-key">STARS</span><span className="meta-val">★ {(selected.stars||0).toLocaleString()}</span></div>
                <div className="meta-row"><span className="meta-key">FORKS</span><span className="meta-val">⑂ {(selected.forks||0).toLocaleString()}</span></div>
                {selected.lang && <div className="meta-row"><span className="meta-key">LANG</span><span className="meta-val">{selected.lang}</span></div>}
              </>
            )}

            {selected.type === 'contributor' && selected.contributions && (
              <div className="meta-row"><span className="meta-key">COMMITS</span><span className="meta-val">{selected.contributions}</span></div>
            )}

            {selected.type === 'user' && (
              <div className="meta-row"><span className="meta-key">ROLE</span><span className="meta-val">PRIMARY TARGET</span></div>
            )}

            {selected.url && (
              <a href={selected.url} target="_blank" rel="noreferrer"
                style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--accent)', border: '1px solid var(--accent-dim)', padding: '4px 8px', textAlign: 'center', display: 'block', marginTop: 10 }}>
                OPEN ON GITHUB →
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
