import React, { useMemo } from 'react'
import { Plus, Calendar, BarChart3, BookOpen, Clock, Edit, Volume2, TrendingUp, ArrowRight } from 'lucide-react'
import { format, parseISO, subDays, isSameDay } from 'date-fns'
import './Dashboard.css'

const Dashboard = ({ entries, onNewEntry, onEditEntry, onViewChange }) => {
  // Calculate statistics
  const stats = useMemo(() => {
    const totalEntries = entries.length
    const textEntries = entries.filter(e => e.type !== 'audio').length
    const audioEntries = entries.filter(e => e.type === 'audio').length
    const lastEntry = entries.length > 0 ? entries[0] : null
    
    // Calculate total words in text entries
    const totalWords = entries
      .filter(e => e.type !== 'audio' && e.content)
      .reduce((total, entry) => {
        const textContent = entry.content.replace(/<[^>]*>/g, '')
        return total + textContent.split(/\s+/).filter(word => word.length > 0).length
      }, 0)

    return {
      totalEntries,
      textEntries,
      audioEntries,
      lastEntry,
      totalWords
    }
  }, [entries])

  // Generate activity data for the last 30 days
  const activityData = useMemo(() => {
    const days = []
    const today = new Date()
    
    for (let i = 29; i >= 0; i--) {
      const date = subDays(today, i)
      const dayEntries = entries.filter(entry => 
        isSameDay(parseISO(entry.createdAt), date)
      ).length
      
      days.push({
        date,
        count: dayEntries,
        label: format(date, 'MMM d'),
        shortLabel: format(date, 'M/d')
      })
    }
    
    return days
  }, [entries])

  // Get random past entry for "On This Day"
  const randomEntry = useMemo(() => {
    if (entries.length === 0) return null
    
    // Try to find an entry from same day in previous years
    const today = new Date()
    const sameDay = entries.find(entry => {
      const entryDate = parseISO(entry.createdAt)
      return entryDate.getMonth() === today.getMonth() && 
             entryDate.getDate() === today.getDate() &&
             entryDate.getFullYear() !== today.getFullYear()
    })
    
    if (sameDay) return sameDay
    
    // Otherwise return a random entry
    return entries[Math.floor(Math.random() * entries.length)]
  }, [entries])

  // Get recent entries (last 5)
  const recentEntries = useMemo(() => {
    return entries.slice(0, 5)
  }, [entries])

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const maxCount = Math.max(...activityData.map(d => d.count), 1)

  const truncateContent = (content, maxLength = 80) => {
    if (!content) return ''
    const textContent = content.replace(/<[^>]*>/g, '')
    if (textContent.length <= maxLength) return textContent
    return textContent.substring(0, maxLength) + '...'
  }

  const handleViewTimeline = () => {
    onViewChange('timeline')
  }

  const handleChartBarClick = (day) => {
    if (day.count > 0) {
      onViewChange('timeline')
    }
  }

  const handleChartBarKeyDown = (e, day) => {
    if ((e.key === 'Enter' || e.key === ' ') && day.count > 0) {
      e.preventDefault()
      onViewChange('timeline')
    }
  }

  const handleMemoryCardKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onEditEntry(randomEntry)
    }
  }

  const handleRecentItemKeyDown = (e, entry) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onEditEntry(entry)
    }
  }

  return (
    <div className="dashboard" role="main" aria-label="Journal Dashboard">
      <header className="dashboard-header">
        <div className="greeting-section">
          <BookOpen className="greeting-icon" aria-hidden="true" />
          <div>
            <h1 id="dashboard-heading">{getGreeting()}</h1>
            <p>Welcome back to your digital sanctuary</p>
          </div>
        </div>
      </header>

      <div className="dashboard-grid" role="region" aria-labelledby="dashboard-heading">
        {/* Primary: Quick Actions - Most prominent */}
        <section 
          className="dashboard-card quick-actions glass-strong priority-one"
          aria-labelledby="quick-actions-heading"
        >
          <header className="card-header">
            <Plus className="card-icon" aria-hidden="true" />
            <h2 id="quick-actions-heading">Start Writing</h2>
          </header>
          <div className="card-content">
            <button
              className="action-btn btn-primary cta-primary"
              onClick={onNewEntry}
              aria-label="Create a new journal entry"
              aria-describedby="new-entry-desc"
            >
              <Edit size={24} aria-hidden="true" />
              <span>Create New Entry</span>
            </button>
            <div id="new-entry-desc" className="sr-only">
              Start writing a new journal entry with text or audio
            </div>
            
            <button
              className="action-btn btn-secondary"
              onClick={handleViewTimeline}
              aria-label="View all journal entries in chronological timeline"
              aria-describedby="timeline-desc"
            >
              <Calendar size={20} aria-hidden="true" />
              <span>View Timeline</span>
              <ArrowRight size={16} aria-hidden="true" />
            </button>
            <div id="timeline-desc" className="sr-only">
              Browse all {stats.totalEntries} journal entries in chronological order
            </div>
          </div>
        </section>

        {/* Secondary: Activity Chart - Dominant visual element */}
        <section 
          className="dashboard-card activity-chart glass-strong priority-two"
          aria-labelledby="activity-chart-heading"
          aria-describedby="activity-chart-desc"
        >
          <header className="card-header">
            <TrendingUp className="card-icon" aria-hidden="true" />
            <h2 id="activity-chart-heading">30-Day Activity</h2>
          </header>
          <div className="card-content">
            <div id="activity-chart-desc" className="sr-only">
              Activity chart showing your journal entry frequency over the last 30 days. 
              Total of {stats.totalEntries} entries. Click on bars to view entries for specific days.
            </div>
            
            <div 
              className="chart-container"
              role="img"
              aria-labelledby="activity-chart-heading"
              aria-describedby="activity-chart-desc"
            >
              <div className="chart-bars" role="list" aria-label="Daily activity bars">
                {activityData.map((day, index) => (
                  <div key={index} className="chart-bar-container" role="listitem">
                    <button 
                      className="chart-bar"
                      style={{ 
                        height: `${Math.max((day.count / maxCount) * 100, 3)}%`,
                        backgroundColor: day.count > 0 ? 'var(--accent-color)' : 'var(--bg-secondary)',
                        opacity: day.count > 0 ? 1 : 0.3
                      }}
                      onClick={() => handleChartBarClick(day)}
                      onKeyDown={(e) => handleChartBarKeyDown(e, day)}
                      aria-label={`${day.label}: ${day.count} ${day.count === 1 ? 'entry' : 'entries'}${day.count > 0 ? '. Press Enter to view entries.' : ''}`}
                      disabled={day.count === 0}
                      tabIndex={day.count > 0 ? 0 : -1}
                      title={`${day.label}: ${day.count} entries`}
                    />
                    {index % 5 === 0 && (
                      <div className="chart-label" aria-hidden="true">
                        {day.shortLabel}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="chart-summary">
              <span>Click bars to view entries for that day</span>
            </div>
          </div>
        </section>

        {/* Tertiary: Statistics */}
        <section 
          className="dashboard-card statistics glass-strong priority-three"
          aria-labelledby="statistics-heading"
          aria-describedby="statistics-desc"
        >
          <header className="card-header">
            <BarChart3 className="card-icon" aria-hidden="true" />
            <h2 id="statistics-heading">Your Journal</h2>
          </header>
          <div className="card-content">
            <div id="statistics-desc" className="sr-only">
              Overview of your journal statistics including total entries, entry types, and word count
            </div>
            
            <div className="stat-grid" role="list" aria-label="Journal statistics">
              <div className="stat-item" role="listitem">
                <div 
                  className="stat-value" 
                  aria-label={`Total entries: ${stats.totalEntries}`}
                >
                  {stats.totalEntries}
                </div>
                <div className="stat-label">Total Entries</div>
              </div>
              <div className="stat-item" role="listitem">
                <div 
                  className="stat-value" 
                  aria-label={`Text entries: ${stats.textEntries}`}
                >
                  {stats.textEntries}
                </div>
                <div className="stat-label">Text Entries</div>
              </div>
              {stats.audioEntries > 0 && (
                <div className="stat-item" role="listitem">
                  <div 
                    className="stat-value" 
                    aria-label={`Audio entries: ${stats.audioEntries}`}
                  >
                    {stats.audioEntries}
                  </div>
                  <div className="stat-label">Audio Entries</div>
                </div>
              )}
              <div className="stat-item" role="listitem">
                <div 
                  className="stat-value" 
                  aria-label={`Total words written: ${stats.totalWords.toLocaleString()}`}
                >
                  {stats.totalWords.toLocaleString()}
                </div>
                <div className="stat-label">Words Written</div>
              </div>
            </div>
            
            {stats.lastEntry && (
              <div 
                className="last-entry-info"
                role="status"
                aria-label={`Last entry was created on ${format(parseISO(stats.lastEntry.createdAt), 'EEEE, MMMM do, yyyy')}`}
              >
                <Clock size={16} aria-hidden="true" />
                <span>
                  Last entry: <time dateTime={stats.lastEntry.createdAt}>
                    {format(parseISO(stats.lastEntry.createdAt), 'MMM d, yyyy')}
                  </time>
                </span>
              </div>
            )}
          </div>
        </section>

        {/* Tertiary: On This Day / Random Entry */}
        {randomEntry && (
          <section 
            className="dashboard-card on-this-day glass-strong priority-three"
            aria-labelledby="memory-heading"
            aria-describedby="memory-desc"
          >
            <header className="card-header">
              <Calendar className="card-icon" aria-hidden="true" />
              <h2 id="memory-heading">From Your Past</h2>
            </header>
            <div className="card-content">
              <div id="memory-desc" className="sr-only">
                A memory from your journal archive to revisit and reflect upon
              </div>
              
              <button 
                className="memory-card"
                onClick={() => onEditEntry(randomEntry)}
                onKeyDown={handleMemoryCardKeyDown}
                aria-label={`View entry from ${format(parseISO(randomEntry.createdAt), 'MMMM do, yyyy')}: ${randomEntry.title || 'Untitled entry'}`}
                aria-describedby="memory-content-desc"
              >
                <div className="memory-header">
                  <div className="memory-meta">
                    <Clock size={14} aria-hidden="true" />
                    <time 
                      dateTime={randomEntry.createdAt}
                      aria-label={`Created on ${format(parseISO(randomEntry.createdAt), 'EEEE, MMMM do, yyyy')}`}
                    >
                      {format(parseISO(randomEntry.createdAt), 'MMM d, yyyy')}
                    </time>
                    {randomEntry.type === 'audio' && (
                      <>
                        <Volume2 size={14} aria-hidden="true" />
                        <span>Audio Entry</span>
                      </>
                    )}
                  </div>
                </div>
                {randomEntry.title && (
                  <h3 className="memory-title" id="memory-content-desc">
                    {randomEntry.title}
                  </h3>
                )}
                {randomEntry.type !== 'audio' && randomEntry.content && (
                  <p className="memory-content">
                    {truncateContent(randomEntry.content)}
                  </p>
                )}
                {randomEntry.type === 'audio' && (
                  <div className="audio-indicator">
                    <Volume2 size={20} aria-hidden="true" />
                    <span>Click to play audio entry</span>
                  </div>
                )}
              </button>
            </div>
          </section>
        )}

        {/* Tertiary: Recent Entries */}
        {recentEntries.length > 0 && (
          <section 
            className="dashboard-card recent-entries glass-strong priority-three"
            aria-labelledby="recent-heading"
            aria-describedby="recent-desc"
          >
            <header className="card-header">
              <BookOpen className="card-icon" aria-hidden="true" />
              <h2 id="recent-heading">Recent Entries</h2>
            </header>
            <div className="card-content">
              <div id="recent-desc" className="sr-only">
                Your most recent journal entries for quick access
              </div>
              
              <div className="recent-list" role="list" aria-label="Recent journal entries">
                {recentEntries.map((entry, index) => (
                  <button 
                    key={entry.id}
                    className="recent-item"
                    onClick={() => onEditEntry(entry)}
                    onKeyDown={(e) => handleRecentItemKeyDown(e, entry)}
                    aria-label={`View entry: ${entry.title || 'Untitled'} from ${format(parseISO(entry.createdAt), 'MMMM do')}. ${index + 1} of ${recentEntries.length}.`}
                    role="listitem"
                  >
                    <div className="recent-header">
                      <div className="recent-meta">
                        <Clock size={12} aria-hidden="true" />
                        <time 
                          dateTime={entry.createdAt}
                          aria-label={format(parseISO(entry.createdAt), 'EEEE, MMMM do')}
                        >
                          {format(parseISO(entry.createdAt), 'MMM d')}
                        </time>
                        {entry.type === 'audio' && (
                          <Volume2 size={12} aria-hidden="true" />
                        )}
                      </div>
                    </div>
                    <div className="recent-title">
                      {entry.title || 'Untitled Entry'}
                    </div>
                    {entry.type !== 'audio' && entry.content && (
                      <div className="recent-preview">
                        {truncateContent(entry.content, 60)}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Live region for dynamic announcements */}
      <div 
        id="dashboard-announcements"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {/* Dynamic content announcements will be inserted here */}
      </div>
    </div>
  )
}

export default Dashboard