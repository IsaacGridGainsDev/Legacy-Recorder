import React, { useState, useEffect } from 'react'
import { Plus, Calendar, Search, Settings, BookOpen, Moon, Sun, Volume2, BarChart3 } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'
import './Sidebar.css'

const Sidebar = ({ 
  currentView, 
  onViewChange, 
  onNewEntry, 
  entriesCount, 
  audioEntriesCount,
  isMobileOpen,
  onCloseMobile
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const menuItems = [
    {
      id: 'dashboard',
      icon: BarChart3,
      label: 'Dashboard',
      description: 'Overview of your journal activity'
    },
    {
      id: 'timeline',
      icon: Calendar,
      label: 'Timeline',
      badge: entriesCount,
      description: `View all ${entriesCount} entries chronologically`
    },
    {
      id: 'search',
      icon: Search,
      label: 'Search',
      description: 'Find specific entries and filter by tags'
    },
    {
      id: 'settings',
      icon: Settings,
      label: 'Settings',
      description: 'Customize your journaling experience'
    }
  ]

  const handleNavClick = (itemId) => {
    onViewChange(itemId)
    if (onCloseMobile) {
      onCloseMobile()
    }
  }

  const handleNewEntryClick = () => {
    onNewEntry()
    if (onCloseMobile) {
      onCloseMobile()
    }
  }

  // Focus management for accessibility
  useEffect(() => {
    if (isMobileOpen) {
      // Focus first interactive element when menu opens
      const firstButton = document.querySelector('.sidebar .new-entry-btn')
      if (firstButton) {
        firstButton.focus()
      }
    }
  }, [isMobileOpen])

  return (
    <aside 
      className={`sidebar glass ${isCollapsed ? 'collapsed' : ''} ${isMobileOpen ? 'mobile-open' : ''}`}
      id="sidebar-navigation"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="sidebar-header">
        <div className="logo">
          <BookOpen className="logo-icon" aria-hidden="true" />
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
          onClick={handleNewEntryClick}
          aria-label="Create new journal entry"
          title="Create new entry"
        >
          <Plus size={20} aria-hidden="true" />
          {!isCollapsed && <span>New Entry</span>}
        </button>

        {!isCollapsed && audioEntriesCount > 0 && (
          <div 
            className="audio-stats glass-subtle"
            role="status"
            aria-label={`You have ${audioEntriesCount} audio entries`}
          >
            <Volume2 size={16} aria-hidden="true" />
            <span>{audioEntriesCount} audio entries</span>
          </div>
        )}

        <nav className="sidebar-nav" role="menubar">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${currentView === item.id ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
              aria-label={item.description}
              aria-current={currentView === item.id ? 'page' : undefined}
              title={item.description}
              role="menuitem"
            >
              <item.icon size={20} aria-hidden="true" />
              {!isCollapsed && (
                <span className="nav-label">
                  <span>{item.label}</span>
                  {item.badge !== undefined && (
                    <span 
                      className="nav-badge"
                      aria-label={`${item.badge} items`}
                    >
                      {item.badge}
                    </span>
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
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
        >
          {theme === 'light' ? 
            <Moon size={20} aria-hidden="true" /> : 
            <Sun size={20} aria-hidden="true" />
          }
          {!isCollapsed && (
            <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
          )}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar