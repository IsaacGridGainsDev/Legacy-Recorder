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

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="greeting-section">
          <BookOpen className="greeting-icon" aria-hidden="true" />
          <div>
            <h1>{getGreeting()}</h1>
            <p>Welcome back to your digital sanctuary</p>
          </div>
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Primary: Quick Actions - Most prominent */}
        <section className="dashboard-card quick-actions glass-strong priority-one">
          <header className="card-header">
            <Plus className="card-icon" aria-hidden="true" />
            <h2>Start Writing</h2>
          </header>
          <div className="card-content">
            <button
              className="action-btn btn-primary cta-primary"
              onClick={onNewEntry}
              aria-label="Create a new journal entry"
            >
              <Edit size={24} aria-hidden="true" />
              <span>Create New Entry</span>
            </button>
            <button
              className="action-btn btn-secondary"
              onClick={handleViewTimeline}
              aria-label="View all journal entries in timeline"
            >
              <Calendar size={20} aria-hidden="true" />
              <span>View Timeline</span>
              <ArrowRight size={16} aria-hidden="true" />
            </button>
          </div>
        </section>

        {/* Secondary: Activity Chart - Dominant visual element */}
        <section 
          className="dashboard-card activity-chart glass-strong priority-two"
          aria-labelledby="activity-chart-heading"
        >
          <header className="card-header">
            <TrendingUp className="card-icon" aria-hidden="true" />
            <h2 id="activity-chart-heading">30-Day Activity</h2>
          </header>
          <div className="card-content">
            <div 
              className="chart-container"
              role="img"
              aria-label={`Activity chart showing ${stats.totalEntries} total entries over the last 30 days`}
            >
              <div className="chart-bars">
                {activityData.map((day, index) => (
                  <div key={index} className="chart-bar-container">
                    <button 
                      className="chart-bar"
                      style={{ 
                        height: `${Math.max((day.count / maxCount) * 100, 3)}%`,
                        backgroundColor: day.count > 0 ? 'var(--accent-color)' : 'var(--bg-secondary)',
                        opacity: day.count > 0 ? 1 : 0.3
                      }}
                      onClick={() => handleChartBarClick(day)}
                      aria-label={`${day.label}: ${day.count} entries${day.count > 0 ? ' - Click to view entries' : ''}`}
                      disabled={day.count === 0}
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
        >
          <header className="card-header">
            <BarChart3 className="card-icon" aria-hidden="true" />
            <h2 id="statistics-heading">Your Journal</h2>
          </header>
          <div className="card-content">
            <div className="stat-grid" role="list">
              <div className="stat-item" role="listitem">
                <div className="stat-value" aria-label="Total entries">{stats.totalEntries}</div>
                <div className="stat-label">Total Entries</div>
              </div>
              <div className="stat-item" role="listitem">
                <div className="stat-value" aria-label="Text entries">{stats.textEntries}</div>
                <div className="stat-label">Text Entries</div>
              </div>
              {stats.audioEntries > 0 && (
                <div className="stat-item" role="listitem">
                  <div className="stat-value" aria-label="Audio entries">{stats.audioEntries}</div>
                  <div className="stat-label">Audio Entries</div>
                </div>
              )}
              <div className="stat-item" role="listitem">
                <div className="stat-value" aria-label={`${stats.totalWords.toLocaleString()} words written`}>
                  {stats.totalWords.toLocaleString()}
                </div>
                <div className="stat-label">Words Written</div>
              </div>
            </div>
            {stats.lastEntry && (
              <div className="last-entry-info">
                <Clock size={16} aria-hidden="true" />
                <span>Last entry: {format(parseISO(stats.lastEntry.createdAt), 'MMM d, yyyy')}</span>
              </div>
            )}
          </div>
        </section>

        {/* Tertiary: On This Day / Random Entry */}
        {randomEntry && (
          <section 
            className="dashboard-card on-this-day glass-strong priority-three"
            aria-labelledby="memory-heading"
          >
            <header className="card-header">
              <Calendar className="card-icon" aria-hidden="true" />
              <h2 id="memory-heading">From Your Past</h2>
            </header>
            <div className="card-content">
              <button 
                className="memory-card"
                onClick={() => onEditEntry(randomEntry)}
                aria-label={`View entry from ${format(parseISO(randomEntry.createdAt), 'MMMM d, yyyy')}: ${randomEntry.title || 'Untitled entry'}`}
              >
                <div className="memory-header">
                  <div className="memory-meta">
                    <Clock size={14} aria-hidden="true" />
                    <time dateTime={randomEntry.createdAt}>
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
                  <h3 className="memory-title">{randomEntry.title}</h3>
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
          >
            <header className="card-header">
              <BookOpen className="card-icon" aria-hidden="true" />
              <h2 id="recent-heading">Recent Entries</h2>
            </header>
            <div className="card-content">
              <div className="recent-list" role="list">
                {recentEntries.map((entry) => (
                  <button 
                    key={entry.id}
                    className="recent-item"
                    onClick={() => onEditEntry(entry)}
                    aria-label={`View entry: ${entry.title || 'Untitled'} from ${format(parseISO(entry.createdAt), 'MMMM d')}`}
                    role="listitem"
                  >
                    <div className="recent-header">
                      <div className="recent-meta">
                        <Clock size={12} aria-hidden="true" />
                        <time dateTime={entry.createdAt}>
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
    </div>
  )
}

export default Dashboard