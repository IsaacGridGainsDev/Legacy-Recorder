import React, { useState, useEffect } from 'react'
import { Plus, Calendar, Search, Settings, BookOpen, Moon, Sun, Volume2, BarChart3, X } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'
import './Sidebar.css'

const Sidebar = ({ 
  currentView, 
  onViewChange, 
  onNewEntry, 
  entriesCount, 
  audioEntriesCount,
  isMobileOpen,
  onCloseMobile,
  onToggleTheme,
  theme
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false)

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

  const handleThemeToggle = () => {
    onToggleTheme()
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

  // Trap focus within sidebar when mobile menu is open
  useEffect(() => {
    if (!isMobileOpen) return

    const sidebar = document.querySelector('.sidebar')
    const focusableElements = sidebar.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleTabKey = (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault()
            lastElement.focus()
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault()
            firstElement.focus()
          }
        }
      }
    }

    document.addEventListener('keydown', handleTabKey)
    return () => document.removeEventListener('keydown', handleTabKey)
  }, [isMobileOpen])

  return (
    <>
      {/* Desktop: Horizontal Navigation */}
      <nav 
        className="horizontal-nav glass"
        role="navigation"
        aria-label="Main navigation"
      >
        <div className="nav-container">
          <div className="nav-brand">
            <BookOpen className="brand-icon" aria-hidden="true" />
            <div className="brand-text">
              <span className="brand-title">Aura Journal</span>
              <span className="brand-subtitle">Digital sanctuary</span>
            </div>
          </div>

          <div className="nav-items">
            {menuItems.map((item) => (
              <button
                key={item.id}
                className={`nav-btn ${currentView === item.id ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
                aria-label={item.description}
                aria-current={currentView === item.id ? 'page' : undefined}
                title={item.description}
              >
                <item.icon size={18} aria-hidden="true" />
                <span className="nav-label">{item.label}</span>
                {item.badge !== undefined && (
                  <span 
                    className="nav-badge"
                    aria-label={`${item.badge} items`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            ))}
          </div>

          <div className="nav-actions">
            <button
              className="new-entry-btn btn-primary"
              onClick={handleNewEntryClick}
              aria-label="Create new journal entry"
              title="Create new entry"
            >
              <Plus size={18} aria-hidden="true" />
              <span>New Entry</span>
            </button>
            
            <button
              className="theme-btn btn-secondary"
              onClick={handleThemeToggle}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
            >
              {theme === 'light' ? 
                <Moon size={18} aria-hidden="true" /> : 
                <Sun size={18} aria-hidden="true" />
              }
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile: Sidebar Overlay */}
      <aside 
        className={`sidebar glass ${isCollapsed ? 'collapsed' : ''} ${isMobileOpen ? 'mobile-open' : ''}`}
        id="main-navigation"
        role="navigation"
        aria-label="Main navigation"
        aria-hidden={!isMobileOpen}
      >
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <BookOpen className="brand-icon" aria-hidden="true" />
            {!isCollapsed && (
              <div className="brand-text">
                <h1 className="brand-title">Aura Journal</h1>
                <span className="brand-subtitle">Your digital sanctuary</span>
              </div>
            )}
          </div>
          
          <button
            className="close-btn"
            onClick={onCloseMobile}
            aria-label="Close navigation menu"
          >
            <X size={20} aria-hidden="true" />
          </button>
        </div>

        <div className="sidebar-content">
          <button
            className="new-entry-btn btn-primary"
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
                  <span className="nav-text">
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
            className="theme-toggle btn-secondary"
            onClick={handleThemeToggle}
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
    </>
  )
}

export default Sidebar