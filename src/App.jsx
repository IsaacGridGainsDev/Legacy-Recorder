import React, { useState, useEffect } from 'react'
import { Menu, X } from 'lucide-react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import Timeline from './components/Timeline'
import EntryEditor from './components/EntryEditor'
import AudioRecorder from './components/AudioRecorder'
import AudioPlayer from './components/AudioPlayer'
import UnifiedEntryModal from './components/UnifiedEntryModal'
import SearchView from './components/SearchView'
import Settings from './components/Settings'
import { useLocalStorage } from './hooks/useLocalStorage'
import { useTheme } from './hooks/useTheme'
import './App.css'

function App() {
  const [entries, setEntries] = useLocalStorage('aura-journal-entries', [])
  const [settings, setSettings] = useLocalStorage('aura-journal-settings', {
    theme: 'light',
    fontSize: 16,
    speechLanguage: 'en-US',
    audioQuality: 'high'
  })
  const [currentView, setCurrentView] = useState('dashboard')
  const [selectedEntry, setSelectedEntry] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isUnifiedModalOpen, setIsUnifiedModalOpen] = useState(false)
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [isRecorderOpen, setIsRecorderOpen] = useState(false)
  const [isPlayerOpen, setIsPlayerOpen] = useState(false)
  const [audioToPlay, setAudioToPlay] = useState(null)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  
  const { theme, toggleTheme } = useTheme(settings.theme)

  // Save entry (create or update)
  const saveEntry = (entryData) => {
    const now = new Date()
    
    if (entryData.id) {
      // Update existing entry
      setEntries(prevEntries => 
        prevEntries.map(entry => 
          entry.id === entryData.id 
            ? { ...entryData, updatedAt: now.toISOString() }
            : entry
        )
      )
    } else {
      // Create new entry
      const newEntry = {
        id: Date.now().toString(),
        ...entryData,
        createdAt: now.toISOString(),
        updatedAt: now.toISOString()
      }
      setEntries(prevEntries => [newEntry, ...prevEntries])
    }
    
    setIsUnifiedModalOpen(false)
    setIsEditorOpen(false)
    setIsRecorderOpen(false)
    setSelectedEntry(null)
  }

  // Delete entry
  const deleteEntry = (entryId) => {
    setEntries(prevEntries => prevEntries.filter(entry => entry.id !== entryId))
    setSelectedEntry(null)
    setIsPlayerOpen(false)
  }

  // Open entry for editing
  const editEntry = (entry) => {
    setSelectedEntry(entry)
    if (entry.type === 'audio') {
      setAudioToPlay(entry)
      setIsPlayerOpen(true)
    } else {
      setIsEditorOpen(true)
    }
    // Close mobile menu when navigating
    setIsMobileMenuOpen(false)
  }

  // Create new entry (unified modal)
  const createNewEntry = () => {
    setSelectedEntry(null)
    setIsUnifiedModalOpen(true)
    // Close mobile menu when creating entry
    setIsMobileMenuOpen(false)
  }

  // Create new audio entry (legacy - for backwards compatibility)
  const createNewAudioEntry = () => {
    setSelectedEntry(null)
    setIsRecorderOpen(true)
  }

  // Play audio entry
  const playAudioEntry = (entry) => {
    setAudioToPlay(entry)
    setIsPlayerOpen(true)
  }

  // Filter entries based on search
  const filteredEntries = entries.filter(entry => {
    if (!searchQuery) return true
    
    const searchLower = searchQuery.toLowerCase()
    return (
      entry.title?.toLowerCase().includes(searchLower) ||
      entry.content?.toLowerCase().includes(searchLower) ||
      entry.transcription?.toLowerCase().includes(searchLower) ||
      entry.tags?.some(tag => tag.toLowerCase().includes(searchLower))
    )
  })

  // Update settings
  const updateSettings = (newSettings) => {
    setSettings(prevSettings => ({ ...prevSettings, ...newSettings }))
  }

  // Handle view change
  const handleViewChange = (view) => {
    setCurrentView(view)
    setIsMobileMenuOpen(false)
  }

  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  // Close mobile menu when clicking overlay
  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  // Apply theme and font size
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.style.setProperty('--user-font-size', `${Math.max(settings.fontSize, 16)}px`)
  }, [theme, settings.fontSize])

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isMobileMenuOpen) {
        setIsMobileMenuOpen(false)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isMobileMenuOpen])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }

    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isMobileMenuOpen])

  // Close menu on window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768 && isMobileMenuOpen) {
        setIsMobileMenuOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [isMobileMenuOpen])

  // Focus management for modals
  useEffect(() => {
    const trapFocus = (e) => {
      if (isUnifiedModalOpen || isEditorOpen || isRecorderOpen || isPlayerOpen) {
        const modal = document.querySelector('.modal-overlay')
        if (!modal) return

        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

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
    }

    document.addEventListener('keydown', trapFocus)
    return () => document.removeEventListener('keydown', trapFocus)
  }, [isUnifiedModalOpen, isEditorOpen, isRecorderOpen, isPlayerOpen])

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <Dashboard
            entries={entries}
            onNewEntry={createNewEntry}
            onEditEntry={editEntry}
            onViewChange={handleViewChange}
          />
        )
      case 'timeline':
        return (
          <Timeline
            entries={filteredEntries}
            onEditEntry={editEntry}
            onDeleteEntry={deleteEntry}
            onPlayAudio={playAudioEntry}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
          />
        )
      case 'search':
        return (
          <SearchView
            entries={entries}
            onEditEntry={editEntry}
            onDeleteEntry={deleteEntry}
            onPlayAudio={playAudioEntry}
          />
        )
      case 'settings':
        return (
          <Settings
            settings={settings}
            onUpdateSettings={updateSettings}
            onToggleTheme={toggleTheme}
            theme={theme}
          />
        )
      default:
        return null
    }
  }

  return (
    <>
      {/* Skip Links for Keyboard Navigation - WCAG AA */}
      <a 
        href="#main-content" 
        className="skip-link sr-only-focusable"
        aria-label="Skip to main content"
      >
        Skip to main content
      </a>
      <a 
        href="#main-navigation" 
        className="skip-link sr-only-focusable"
        aria-label="Skip to navigation"
      >
        Skip to navigation
      </a>

      <div 
        className={`app ${isMobileMenuOpen ? 'menu-open' : ''}`}
        role="application"
        aria-label="Aura Journal Application"
      >
        {/* Mobile menu toggle button */}
        <button
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
          aria-label={isMobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
          aria-expanded={isMobileMenuOpen}
          aria-controls="main-navigation"
          aria-haspopup="true"
        >
          {isMobileMenuOpen ? (
            <X size={20} aria-hidden="true" />
          ) : (
            <Menu size={20} aria-hidden="true" />
          )}
          <span className="sr-only">
            {isMobileMenuOpen ? 'Close' : 'Open'} navigation menu
          </span>
        </button>

        {/* Mobile menu overlay */}
        {isMobileMenuOpen && (
          <div 
            className="mobile-overlay"
            onClick={closeMobileMenu}
            aria-hidden="true"
            role="presentation"
          />
        )}

        <Sidebar
          currentView={currentView}
          onViewChange={handleViewChange}
          onNewEntry={createNewEntry}
          entriesCount={entries.length}
          audioEntriesCount={entries.filter(e => e.type === 'audio').length}
          isMobileOpen={isMobileMenuOpen}
          onCloseMobile={closeMobileMenu}
          onToggleTheme={toggleTheme}
          theme={theme}
        />
        
        <main 
          id="main-content"
          className="main-content"
          role="main"
          aria-label="Main content area"
          tabIndex={-1}
        >
          <div 
            role="region" 
            aria-live="polite" 
            aria-atomic="true" 
            className="sr-only"
            id="status-announcements"
          >
            {/* Dynamic status announcements for screen readers */}
          </div>
          
          {renderCurrentView()}
        </main>

        {/* Modal Management with Focus Trapping */}
        {isUnifiedModalOpen && (
          <div 
            role="dialog"
            aria-modal="true"
            aria-labelledby="unified-modal-title"
            aria-describedby="unified-modal-description"
            className="focus-trap"
          >
            <UnifiedEntryModal
              onSave={saveEntry}
              onCancel={() => {
                setIsUnifiedModalOpen(false)
                setSelectedEntry(null)
              }}
              speechLanguage={settings.speechLanguage}
              audioQuality={settings.audioQuality}
            />
          </div>
        )}

        {isEditorOpen && (
          <div 
            role="dialog"
            aria-modal="true"
            aria-labelledby="entry-editor-title"
            aria-describedby="entry-editor-description"
            className="focus-trap"
          >
            <EntryEditor
              entry={selectedEntry}
              onSave={saveEntry}
              onCancel={() => {
                setIsEditorOpen(false)
                setSelectedEntry(null)
              }}
              speechLanguage={settings.speechLanguage}
            />
          </div>
        )}

        {isRecorderOpen && (
          <div 
            role="dialog"
            aria-modal="true"
            aria-labelledby="audio-recorder-title"
            aria-describedby="audio-recorder-description"
            className="focus-trap"
          >
            <AudioRecorder
              entry={selectedEntry}
              onSave={saveEntry}
              onCancel={() => {
                setIsRecorderOpen(false)
                setSelectedEntry(null)
              }}
              audioQuality={settings.audioQuality}
            />
          </div>
        )}

        {isPlayerOpen && audioToPlay && (
          <div 
            role="dialog"
            aria-modal="true"
            aria-labelledby="audio-player-title"
            aria-describedby="audio-player-description"
            className="focus-trap"
          >
            <AudioPlayer
              entry={audioToPlay}
              onClose={() => {
                setIsPlayerOpen(false)
                setAudioToPlay(null)
              }}
              onEdit={() => {
                setIsPlayerOpen(false)
                setSelectedEntry(audioToPlay)
                setIsRecorderOpen(true)
              }}
              onDelete={() => deleteEntry(audioToPlay.id)}
            />
          </div>
        )}

        {/* Live Region for Dynamic Content Updates */}
        <div 
          id="live-region"
          aria-live="polite"
          aria-atomic="false"
          className="sr-only"
        >
          {/* Content for screen reader announcements */}
        </div>
      </div>
    </>
  )
}

export default App