import React, { useState, useEffect } from 'react'
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
  }

  // Create new entry (unified modal)
  const createNewEntry = () => {
    setSelectedEntry(null)
    setIsUnifiedModalOpen(true)
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

  // Apply theme and font size
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.style.setProperty('--user-font-size', `${settings.fontSize}px`)
  }, [theme, settings.fontSize])

  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <Dashboard
            entries={entries}
            onNewEntry={createNewEntry}
            onEditEntry={editEntry}
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
    <div className="app">
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        onNewEntry={createNewEntry}
        entriesCount={entries.length}
        audioEntriesCount={entries.filter(e => e.type === 'audio').length}
      />
      
      <main className="main-content">
        {renderCurrentView()}
      </main>

      {isUnifiedModalOpen && (
        <UnifiedEntryModal
          onSave={saveEntry}
          onCancel={() => {
            setIsUnifiedModalOpen(false)
            setSelectedEntry(null)
          }}
          speechLanguage={settings.speechLanguage}
          audioQuality={settings.audioQuality}
        />
      )}

      {isEditorOpen && (
        <EntryEditor
          entry={selectedEntry}
          onSave={saveEntry}
          onCancel={() => {
            setIsEditorOpen(false)
            setSelectedEntry(null)
          }}
          speechLanguage={settings.speechLanguage}
        />
      )}

      {isRecorderOpen && (
        <AudioRecorder
          entry={selectedEntry}
          onSave={saveEntry}
          onCancel={() => {
            setIsRecorderOpen(false)
            setSelectedEntry(null)
          }}
          audioQuality={settings.audioQuality}
        />
      )}

      {isPlayerOpen && audioToPlay && (
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
      )}
    </div>
  )
}

export default App