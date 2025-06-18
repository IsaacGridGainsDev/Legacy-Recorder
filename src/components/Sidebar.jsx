import React, { useState } from 'react'
import { Plus, Calendar, Search, Settings, BookOpen, Moon, Sun, Volume2, BarChart3 } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'
import './Sidebar.css'

const Sidebar = ({ 
  currentView, 
  onViewChange, 
  onNewEntry, 
  entriesCount, 
  audioEntriesCount 
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const menuItems = [
    {
      id: 'dashboard',
      icon: BarChart3,
      label: 'Dashboard'
    },
    {
      id: 'timeline',
      icon: Calendar,
      label: 'Timeline',
      badge: entriesCount
    },
    {
      id: 'search',
      icon: Search,
      label: 'Search'
    },
    {
      id: 'settings',
      icon: Settings,
      label: 'Settings'
    }
  ]

  return (
    <aside className={`sidebar glass ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo">
          <BookOpen className="logo-icon" />
          {!isCollapsed && (
            <div className="logo-text">
              <h1>Aura Journal</h1>
              <span>Your digital sanctuary</span>
            </div>
          )}
        </div>
      </div>

      <div className="sidebar-content">
        <button
          className="btn btn-primary new-entry-btn"
          onClick={onNewEntry}
          title="Create new entry"
        >
          <Plus size={20} />
          {!isCollapsed && 'New Entry'}
        </button>

        {!isCollapsed && audioEntriesCount > 0 && (
          <div className="audio-stats glass-subtle">
            <Volume2 size={16} />
            <span>{audioEntriesCount} audio entries</span>
          </div>
        )}

        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${currentView === item.id ? 'active' : ''}`}
              onClick={() => onViewChange(item.id)}
              title={item.label}
            >
              <item.icon size={20} />
              {!isCollapsed && (
                <span className="nav-label">
                  {item.label}
                  {item.badge !== undefined && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      <div className="sidebar-footer">
        <button
          className="theme-toggle btn btn-secondary"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
        >
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          {!isCollapsed && (theme === 'light' ? 'Dark Mode' : 'Light Mode')}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar