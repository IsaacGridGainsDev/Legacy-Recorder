import React, { useMemo } from 'react'
import { Plus, Calendar, BarChart3, BookOpen, Clock, Edit, Volume2, TrendingUp } from 'lucide-react'
import { format, parseISO, subDays, isAfter, isSameDay } from 'date-fns'
import './Dashboard.css'

const Dashboard = ({ entries, onNewEntry, onEditEntry }) => {
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
        label: format(date, 'MMM d')
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

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="greeting-section">
          <BookOpen className="greeting-icon" />
          <div>
            <h1>{getGreeting()}</h1>
            <p>Welcome back to your digital sanctuary</p>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Quick Actions */}
        <div className="dashboard-card quick-actions glass-strong">
          <div className="card-header">
            <Plus className="card-icon" />
            <h2>Quick Actions</h2>
          </div>
          <div className="card-content">
            <button
              className="action-btn btn-primary"
              onClick={onNewEntry}
            >
              <Edit size={20} />
              <span>Create New Entry</span>
            </button>
            <button
              className="action-btn btn-secondary"
              onClick={() => window.location.hash = '#timeline'}
            >
              <Calendar size={20} />
              <span>View Timeline</span>
            </button>
          </div>
        </div>

        {/* Statistics */}
        <div className="dashboard-card statistics glass-strong">
          <div className="card-header">
            <BarChart3 className="card-icon" />
            <h2>Your Journal</h2>
          </div>
          <div className="card-content">
            <div className="stat-grid">
              <div className="stat-item">
                <div className="stat-value">{stats.totalEntries}</div>
                <div className="stat-label">Total Entries</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{stats.textEntries}</div>
                <div className="stat-label">Text Entries</div>
              </div>
              {stats.audioEntries > 0 && (
                <div className="stat-item">
                  <div className="stat-value">{stats.audioEntries}</div>
                  <div className="stat-label">Audio Entries</div>
                </div>
              )}
              <div className="stat-item">
                <div className="stat-value">{stats.totalWords.toLocaleString()}</div>
                <div className="stat-label">Words Written</div>
              </div>
            </div>
            {stats.lastEntry && (
              <div className="last-entry-info">
                <Clock size={16} />
                <span>Last entry: {format(parseISO(stats.lastEntry.createdAt), 'MMM d, yyyy')}</span>
              </div>
            )}
          </div>
        </div>

        {/* Activity Chart */}
        <div className="dashboard-card activity-chart glass-strong">
          <div className="card-header">
            <TrendingUp className="card-icon" />
            <h2>30-Day Activity</h2>
          </div>
          <div className="card-content">
            <div className="chart-container">
              <div className="chart-bars">
                {activityData.map((day, index) => (
                  <div key={index} className="chart-bar-container">
                    <div 
                      className="chart-bar"
                      style={{ 
                        height: `${(day.count / maxCount) * 100}%`,
                        backgroundColor: day.count > 0 ? 'var(--accent-color)' : 'var(--bg-secondary)'
                      }}
                      title={`${day.label}: ${day.count} entries`}
                    />
                    {index % 5 === 0 && (
                      <div className="chart-label">{format(day.date, 'M/d')}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="chart-summary">
              <span>Hover over bars to see daily counts</span>
            </div>
          </div>
        </div>

        {/* On This Day / Random Entry */}
        {randomEntry && (
          <div className="dashboard-card on-this-day glass-strong">
            <div className="card-header">
              <Calendar className="card-icon" />
              <h2>From Your Past</h2>
            </div>
            <div className="card-content">
              <div 
                className="memory-card"
                onClick={() => onEditEntry(randomEntry)}
              >
                <div className="memory-header">
                  <div className="memory-meta">
                    <Clock size={14} />
                    <span>{format(parseISO(randomEntry.createdAt), 'MMM d, yyyy')}</span>
                    {randomEntry.type === 'audio' && (
                      <>
                        <Volume2 size={14} />
                        <span>Audio Entry</span>
                      </>
                    )}
                  </div>
                </div>
                {randomEntry.title && (
                  <h4 className="memory-title">{randomEntry.title}</h4>
                )}
                {randomEntry.type !== 'audio' && randomEntry.content && (
                  <p className="memory-content">
                    {truncateContent(randomEntry.content)}
                  </p>
                )}
                {randomEntry.type === 'audio' && (
                  <div className="audio-indicator">
                    <Volume2 size={20} />
                    <span>Click to play audio entry</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Recent Entries */}
        {recentEntries.length > 0 && (
          <div className="dashboard-card recent-entries glass-strong">
            <div className="card-header">
              <BookOpen className="card-icon" />
              <h2>Recent Entries</h2>
            </div>
            <div className="card-content">
              <div className="recent-list">
                {recentEntries.map((entry) => (
                  <div 
                    key={entry.id}
                    className="recent-item"
                    onClick={() => onEditEntry(entry)}
                  >
                    <div className="recent-header">
                      <div className="recent-meta">
                        <Clock size={12} />
                        <span>{format(parseISO(entry.createdAt), 'MMM d')}</span>
                        {entry.type === 'audio' && <Volume2 size={12} />}
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
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard