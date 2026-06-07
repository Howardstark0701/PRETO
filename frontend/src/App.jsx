import { useState } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  Search, Users, BarChart2, Brain, Settings,
  Shield, Activity, GitBranch, Globe, Menu, X
} from 'lucide-react'
import SearchPage      from './pages/SearchPage'
import UserPage        from './pages/UserPage'
import InsightsPage    from './pages/InsightsPage'
import AnalyticsPage   from './pages/AnalyticsPage'
import SourcesPage     from './pages/SourcesPage'
import SystemPage      from './pages/SystemPage'
import AuthPage        from './pages/AuthPage'
import GraphPage       from './pages/GraphPage'
import './App.css'

const NAV = [
  { to: '/',          icon: Search,    label: 'Search'     },
  { to: '/user',      icon: Users,     label: 'User Intel' },
  { to: '/graph',     icon: GitBranch, label: 'Graph'      },
  { to: '/insights',  icon: Brain,     label: 'AI Insights'},
  { to: '/sources',   icon: Globe,     label: 'Sources'    },
  { to: '/analytics', icon: BarChart2, label: 'Analytics'  },
  { to: '/system',    icon: Settings,  label: 'System'     },
  { to: '/auth',      icon: Shield,    label: 'Auth'       },
]

export default function App() {
  const loc = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

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
        <div className="sidebar-label">INTELLIGENCE PLATFORM</div>
        <nav className="sidebar-nav">
          {NAV.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              onClick={closeSidebar}
            >
              <Icon size={15} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <Activity size={11} className="pulse-dot" />
          <span>API LIVE</span>
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
