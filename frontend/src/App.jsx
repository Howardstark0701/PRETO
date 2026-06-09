import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  Search, Users, BarChart2, Brain, Settings,
  Shield, Activity, GitBranch, Globe, Menu, X, Radio
} from 'lucide-react'
import SearchPage      from './pages/SearchPage'
import UserPage        from './pages/UserPage'
import InsightsPage    from './pages/InsightsPage'
import AnalyticsPage   from './pages/AnalyticsPage'
import SourcesPage     from './pages/SourcesPage'
import SystemPage      from './pages/SystemPage'
import AuthPage        from './pages/AuthPage'
import GraphPage       from './pages/GraphPage'
import { auth }        from './api'
import './App.css'

const NAV_ITEMS = [
  { to: '/',          icon: Search,   label: 'SEARCH'    },
  { to: '/user',      icon: Users,    label: 'USER INTEL' },
  { to: '/sources',   icon: Globe,    label: 'SOURCES'   },
  { to: '/graph',     icon: GitBranch,label: 'GRAPH'     },
  { to: '/insights',  icon: Brain,    label: 'INSIGHTS'  },
  { to: '/analytics', icon: BarChart2,label: 'ANALYTICS' },
  { to: '/system',    icon: Settings, label: 'SYSTEM'    },
  { to: '/auth',      icon: Shield,   label: 'AUTH'      },
]

export default function App() {
  const loc = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [connStatus, setConnStatus] = useState('CHECKING')

  useEffect(() => {
    let cancelled = false
    async function check() {
      try {
        const { default: { misc } } = await import('./api')
        // Use a simple fetch to check health
        const res = await fetch('/api/health')
        if (!cancelled) setConnStatus(res.ok ? 'LIVE' : 'ERR')
      } catch {
        if (!cancelled) setConnStatus('OFF')
      }
    }
    check()
    const iv = setInterval(check, 30000)
    return () => { cancelled = true; clearInterval(iv) }
  }, [])

  function closeSidebar() { setSidebarOpen(false) }

  return (
    <div className="app-shell">
      <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle sidebar">
        {sidebarOpen ? <X size={16} /> : <Menu size={16} />}
      </button>
      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={closeSidebar} />
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <span className="logo-mark">P</span>
          <span className="logo-text">RETO</span>
        </div>
        <div className="sidebar-label">INTELLIGENCE PLATFORM v4.2.0</div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={closeSidebar}
            >
              <Icon size={14} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <Radio size={10} className="pulse-dot" />
          <span>UPLINK: {connStatus}</span>
        </div>
      </aside>

      <main className="main-content">
        <Routes>
          <Route path="/"                element={<SearchPage />} />
          <Route path="/user"            element={<UserPage />} />
          <Route path="/insights"        element={<InsightsPage />} />
          <Route path="/sources"         element={<SourcesPage />} />
          <Route path="/analytics"       element={<AnalyticsPage />} />
          <Route path="/system"          element={<SystemPage />} />
          <Route path="/auth"            element={<AuthPage />} />
          <Route path="/auth/callback"   element={<AuthPage />} />
          <Route path="/graph"           element={<GraphPage />} />
        </Routes>
      </main>
    </div>
  )
}
