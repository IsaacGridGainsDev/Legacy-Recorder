import React from 'react'
import { Calendar, Clock, Tag, Edit, Trash2, Search, Play, Volume2 } from 'lucide-react'
import { format, isToday, isYesterday, parseISO } from 'date-fns'
import './Timeline.css'

const Timeline = ({ entries, onEditEntry, onDeleteEntry, onPlayAudio, searchQuery, onSearchChange }) => {
  const formatDate = (dateString) => {
    const date = parseISO(dateString)
    
    if (isToday(date)) {
      return `Today, ${format(date, 'h:mm a')}`
    } else if (isYesterday(date)) {
      return `Yesterday, ${format(date, 'h:mm a')}`
    } else {
      return format(date, 'MMM d, yyyy • h:mm a')
    }
  }

  const truncateContent = (content, maxLength = 200) => {
    if (!content) return ''
    
    // Remove HTML tags for preview
    const textContent = content.replace(/<[^>]*>/g, '')
    
    if (textContent.length <= maxLength) return textContent
    return textContent.substring(0, maxLength) + '...'
  }

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleDeleteClick = (e, entryId) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
      onDeleteEntry(entryId)
    }
  }

  const handleEditClick = (e, entry) => {
    e.stopPropagation()
    onEditEntry(entry)
  }

  const handlePlayClick = (e, entry) => {
    e.stopPropagation()
    onPlayAudio(entry)
  }

  const handleCardKeyDown = (e, entry) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onEditEntry(entry)
    }
  }

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Escape') {
      onSearchChange('')
    }
  }

  return (
    <div className="timeline">
      <header className="timeline-header">
        <div className="timeline-title">
          <Calendar className="header-icon" aria-hidden="true" />
          <div>
            <h1 id="timeline-heading">Your Journal Timeline</h1>
            <p>A chronological view of your thoughts and reflections</p>
          </div>
        </div>
        
        <div className="search-container" role="search">
          <label htmlFor="timeline-search" className="sr-only">
            Search journal entries
          </label>
          <Search className="search-icon" aria-hidden="true" />
          <input
            id="timeline-search"
            type="search"
            placeholder="Search entries..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            className="input search-input"
            aria-describedby="search-help"
            autoComplete="off"
            spellCheck="false"
          />
          <div id="search-help" className="sr-only">
            Search through your journal entries by title, content, or tags. Press Escape to clear search.
          </div>
        </div>
      </header>

      <main className="timeline-content" role="main">
        {entries.length === 0 ? (
          <div 
            className="empty-state glass card"
            role="status"
            aria-live="polite"
          >
            <Calendar size={48} className="empty-icon" aria-hidden="true" />
            <h2>No entries yet</h2>
            <p>Start your journaling journey by creating your first entry.</p>
          </div>
        ) : (
          <>
            <div 
              className="results-summary sr-only"
              role="status"
              aria-live="polite"
              aria-atomic="true"
            >
              {searchQuery 
                ? `Found ${entries.length} entries matching "${searchQuery}"`
                : `Showing ${entries.length} journal entries`
              }
            </div>
            
            <div 
              className="entries-grid" 
              role="list" 
              aria-label="Journal entries"
              aria-describedby="timeline-heading"
            >
              {entries.map((entry, index) => (
                <article
                  key={entry.id}
                  className={`entry-card glass card fade-in ${entry.type === 'audio' ? 'audio-entry' : ''}`}
                  onClick={() => onEditEntry(entry)}
                  role="listitem"
                  tabIndex={0}
                  onKeyDown={(e) => handleCardKeyDown(e, entry)}
                  aria-label={`${entry.type === 'audio' ? 'Audio' : 'Text'} entry: ${entry.title || 'Untitled'} from ${formatDate(entry.createdAt)}. ${index + 1} of ${entries.length}.`}
                  aria-describedby={`entry-meta-${entry.id}`}
                >
                  <header className="entry-header">
                    <div 
                      className="entry-meta"
                      id={`entry-meta-${entry.id}`}
                    >
                      <Clock size={16} aria-hidden="true" />
                      <time 
                        dateTime={entry.createdAt}
                        aria-label={`Created on ${format(parseISO(entry.createdAt), 'EEEE, MMMM do, yyyy \'at\' h:mm a')}`}
                      >
                        {formatDate(entry.createdAt)}
                      </time>
                      {entry.type === 'audio' && (
                        <>
                          <Volume2 size={14} aria-hidden="true" />
                          <span aria-label={`Duration: ${formatDuration(entry.duration)}`}>
                            {formatDuration(entry.duration)}
                          </span>
                        </>
                      )}
                    </div>
                    
                    <div 
                      className="entry-actions"
                      role="group"
                      aria-label="Entry actions"
                    >
                      {entry.type === 'audio' && (
                        <button
                          className="btn btn-primary btn-icon"
                          onClick={(e) => handlePlayClick(e, entry)}
                          aria-label={`Play audio entry: ${entry.title || 'Untitled'}`}
                          title="Play audio"
                        >
                          <Play size={16} aria-hidden="true" />
                          <span className="sr-only">Play</span>
                        </button>
                      )}
                      <button
                        className="btn btn-secondary btn-icon"
                        onClick={(e) => handleEditClick(e, entry)}
                        aria-label={entry.type === 'audio' 
                          ? `View details for audio entry: ${entry.title || 'Untitled'}` 
                          : `Edit text entry: ${entry.title || 'Untitled'}`
                        }
                        title={entry.type === 'audio' ? 'View audio entry details' : 'Edit entry'}
                      >
                        <Edit size={16} aria-hidden="true" />
                        <span className="sr-only">
                          {entry.type === 'audio' ? 'View Details' : 'Edit'}
                        </span>
                      </button>
                      <button
                        className="btn btn-danger btn-icon"
                        onClick={(e) => handleDeleteClick(e, entry.id)}
                        aria-label={`Delete entry: ${entry.title || 'Untitled'}. This action cannot be undone.`}
                        title="Delete entry permanently"
                      >
                        <Trash2 size={16} aria-hidden="true" />
                        <span className="sr-only">Delete</span>
                      </button>
                    </div>
                  </header>

                  <div 
                    className="entry-type-indicator" 
                    aria-hidden="true"
                    role="presentation"
                  >
                    {entry.type === 'audio' ? (
                      <Volume2 size={20} className="type-icon audio" />
                    ) : (
                      <Edit size={20} className="type-icon text" />
                    )}
                  </div>

                  {entry.title && (
                    <h2 className="entry-title" id={`entry-title-${entry.id}`}>
                      {entry.title}
                    </h2>
                  )}

                  {entry.type === 'audio' ? (
                    <div className="entry-preview audio-preview">
                      <div 
                        className="audio-waveform" 
                        aria-hidden="true"
                        role="presentation"
                      >
                        {[...Array(8)].map((_, i) => (
                          <div key={i} className="wave-bar"></div>
                        ))}
                      </div>
                      <span 
                        className="audio-duration"
                        aria-label={`Audio duration: ${formatDuration(entry.duration)}`}
                      >
                        {formatDuration(entry.duration)}
                      </span>
                    </div>
                  ) : (
                    entry.content && (
                      <div 
                        className="entry-preview"
                        aria-describedby={`entry-title-${entry.id}`}
                      >
                        {truncateContent(entry.content)}
                      </div>
                    )
                  )}

                  {entry.tags && entry.tags.length > 0 && (
                    <footer className="entry-tags">
                      <Tag size={14} aria-hidden="true" />
                      <div 
                        className="tags-list" 
                        role="list" 
                        aria-label={`Tags: ${entry.tags.join(', ')}`}
                      >
                        {entry.tags.map((tag, tagIndex) => (
                          <span 
                            key={tagIndex} 
                            className="tag" 
                            role="listitem"
                            aria-label={`Tag: ${tag}`}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </footer>
                  )}
                </article>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default Timeline