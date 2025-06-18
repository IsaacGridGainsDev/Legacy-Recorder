import React, { useState, useRef, useEffect } from 'react'
import { X, Edit, Mic, Save, Calendar, Tag, Play, Pause, Square, Volume2, MicOff } from 'lucide-react'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'
import './UnifiedEntryModal.css'

const UnifiedEntryModal = ({ onSave, onCancel, speechLanguage = 'en-US', audioQuality = 'high' }) => {
  const [mode, setMode] = useState('text') // 'text' or 'voice'
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tags, setTags] = useState('')
  const [entryDate, setEntryDate] = useState('')
  
  // Voice mode states
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioURL, setAudioURL] = useState(null)
  const [duration, setDuration] = useState(0)
  const [recordingTime, setRecordingTime] = useState(0)
  const [error, setError] = useState('')
  
  // Speech recognition states
  const [isListening, setIsListening] = useState(false)
  const [speechSupported, setSpeechSupported] = useState(false)
  
  const titleInputRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const intervalRef = useRef(null)
  const audioRef = useRef(null)
  const recognitionRef = useRef(null)

  useEffect(() => {
    // Set current date
    const now = new Date()
    setEntryDate(now.toISOString().split('T')[0])
    
    // Check speech recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    setSpeechSupported(!!SpeechRecognition)

    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = true
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = speechLanguage

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          }
        }

        if (finalTranscript) {
          setContent(prevContent => {
            const textContent = prevContent.replace(/<[^>]*>/g, '')
            const newContent = textContent + (textContent ? ' ' : '') + finalTranscript
            return `<p>${newContent}</p>`
          })
        }
      }

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }
    
    // Focus on title input
    setTimeout(() => {
      titleInputRef.current?.focus()
    }, 100)

    return () => {
      if (recognitionRef.current && isListening) {
        recognitionRef.current.stop()
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [speechLanguage])

  const toggleMode = (newMode) => {
    // Reset states when switching modes
    if (newMode !== mode) {
      if (mode === 'voice') {
        // Stop recording if switching away from voice
        if (isRecording) {
          stopRecording()
        }
        setAudioBlob(null)
        setAudioURL(null)
        setRecordingTime(0)
      }
      if (mode === 'text' && isListening) {
        // Stop speech recognition if switching away from text
        toggleSpeechRecognition()
      }
      setMode(newMode)
    }
  }

  const toggleSpeechRecognition = () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in your browser.')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  const startRecording = async () => {
    try {
      setError('')
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: audioQuality === 'high' ? 44100 : 22050
        } 
      })
      
      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
        ? 'audio/webm;codecs=opus' 
        : 'audio/webm'
      
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType })
      audioChunksRef.current = []
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }
      
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: mimeType })
        setAudioBlob(blob)
        setAudioURL(URL.createObjectURL(blob))
        
        // Stop all tracks to free up the microphone
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorderRef.current.start(100)
      setIsRecording(true)
      setRecordingTime(0)
      
      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
    } catch (err) {
      setError('Failed to access microphone. Please check permissions.')
      console.error('Error accessing microphone:', err)
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume()
        intervalRef.current = setInterval(() => {
          setRecordingTime(prev => prev + 1)
        }, 1000)
      } else {
        mediaRecorderRef.current.pause()
        clearInterval(intervalRef.current)
      }
      setIsPaused(!isPaused)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      clearInterval(intervalRef.current)
    }
  }

  const handleAudioLoad = () => {
    if (audioRef.current) {
      setDuration(Math.round(audioRef.current.duration))
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleSave = async () => {
    if (mode === 'text') {
      if (!title.trim() && !content.trim()) {
        alert('Please add a title or content before saving.')
        return
      }

      const entryData = {
        type: 'text',
        title: title.trim(),
        content: content,
        tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        createdAt: new Date(entryDate).toISOString()
      }

      onSave(entryData)
    } else {
      if (!audioBlob) {
        alert('Please record audio before saving.')
        return
      }

      // Convert blob to base64 for localStorage
      const reader = new FileReader()
      reader.onload = () => {
        const entryData = {
          type: 'audio',
          title: title.trim() || 'Untitled Audio Entry',
          audioData: reader.result,
          duration: duration,
          tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
          createdAt: new Date(entryDate).toISOString()
        }
        onSave(entryData)
      }
      reader.readAsDataURL(audioBlob)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      if (isListening) {
        toggleSpeechRecognition()
      } else {
        onCancel()
      }
    } else if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      handleSave()
    }
  }

  const canSave = mode === 'text' 
    ? (title.trim() || content.trim())
    : audioBlob

  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['blockquote', 'code-block'],
      ['link'],
      ['clean']
    ],
  }

  const formats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'blockquote', 'code-block', 'link'
  ]

  return (
    <div className="modal-overlay" onKeyDown={handleKeyDown}>
      <div className="unified-entry-modal glass-strong">
        <div className="modal-header">
          <h2>Create New Entry</h2>
          <div className="header-actions">
            <button
              className="btn btn-secondary"
              onClick={onCancel}
              title="Cancel (Esc)"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="mode-toggle-container">
          <div className="mode-toggle glass">
            <button
              className={`toggle-btn ${mode === 'text' ? 'active' : ''}`}
              onClick={() => toggleMode('text')}
            >
              <Edit size={20} />
              <span>Text Entry</span>
            </button>
            <button
              className={`toggle-btn ${mode === 'voice' ? 'active' : ''}`}
              onClick={() => toggleMode('voice')}
            >
              <Mic size={20} />
              <span>Voice Entry</span>
            </button>
            <div className={`toggle-indicator ${mode}`}></div>
          </div>
        </div>

        <div className="modal-content">
          <div className="entry-meta">
            <div className="input-group">
              <Calendar size={18} />
              <input
                type="date"
                value={entryDate}
                onChange={(e) => setEntryDate(e.target.value)}
                className="input date-input"
              />
            </div>
          </div>

          <div className="input-group">
            <input
              ref={titleInputRef}
              type="text"
              placeholder={mode === 'text' ? "Give your entry a title..." : "Give your audio entry a title..."}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input title-input"
            />
          </div>

          <div className={`content-area ${mode}-mode`}>
            {mode === 'text' ? (
              <div className="text-content">
                {speechSupported && (
                  <div className="text-controls">
                    <button
                      className={`btn ${isListening ? 'btn-danger' : 'btn-secondary'} speech-btn`}
                      onClick={toggleSpeechRecognition}
                      title={isListening ? 'Stop dictation' : 'Start dictation'}
                    >
                      {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                      {isListening ? 'Stop Dictation' : 'Dictate'}
                    </button>
                  </div>
                )}

                {isListening && (
                  <div className="speech-indicator glass">
                    <div className="listening-animation">
                      <div className="sound-wave"></div>
                      <div className="sound-wave"></div>
                      <div className="sound-wave"></div>
                    </div>
                    <span>Listening... Speak now</span>
                  </div>
                )}

                <div className="editor-wrapper">
                  <ReactQuill
                    theme="snow"
                    value={content}
                    onChange={setContent}
                    modules={modules}
                    formats={formats}
                    placeholder="What's on your mind today? Share your thoughts, reflections, or experiences..."
                  />
                </div>
              </div>
            ) : (
              <div className="voice-content">
                {error && (
                  <div className="error-message">
                    <span>{error}</span>
                  </div>
                )}

                <div className="recording-section glass">
                  <div className="recording-controls">
                    {!isRecording && !audioURL && (
                      <button
                        className="btn btn-primary record-btn"
                        onClick={startRecording}
                      >
                        <Mic size={24} />
                        Start Recording
                      </button>
                    )}

                    {isRecording && (
                      <div className="recording-active">
                        <div className="recording-indicator">
                          <div className={`recording-dot ${isPaused ? 'paused' : ''}`}></div>
                          <span className="recording-time">{formatTime(recordingTime)}</span>
                        </div>
                        
                        <div className="recording-buttons">
                          <button
                            className="btn btn-secondary"
                            onClick={pauseRecording}
                          >
                            {isPaused ? <Play size={20} /> : <Pause size={20} />}
                            {isPaused ? 'Resume' : 'Pause'}
                          </button>
                          
                          <button
                            className="btn btn-danger"
                            onClick={stopRecording}
                          >
                            <Square size={20} />
                            Stop
                          </button>
                        </div>
                      </div>
                    )}

                    {audioURL && (
                      <div className="audio-preview">
                        <div className="audio-info">
                          <Volume2 size={20} />
                          <span>Duration: {formatTime(duration)}</span>
                        </div>
                        
                        <audio
                          ref={audioRef}
                          src={audioURL}
                          controls
                          className="audio-player"
                          onLoadedMetadata={handleAudioLoad}
                        />
                        
                        <button
                          className="btn btn-secondary"
                          onClick={() => {
                            setAudioBlob(null)
                            setAudioURL(null)
                            setDuration(0)
                            setRecordingTime(0)
                          }}
                        >
                          Record Again
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="input-group">
            <Tag size={18} />
            <input
              type="text"
              placeholder="Add tags (separated by commas)"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="input tags-input"
            />
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-content">
            <div className="entry-tips">
              <span>💡 Tip: Use <kbd>Ctrl+S</kbd> to save or <kbd>Esc</kbd> to cancel</span>
              {mode === 'text' && speechSupported && (
                <span>🎙️ Click "Dictate" to use voice input</span>
              )}
            </div>
            <button
              className="btn btn-primary save-btn"
              onClick={handleSave}
              disabled={!canSave}
              title="Save entry"
            >
              <Save size={20} />
              Save {mode === 'text' ? 'Text' : 'Audio'} Entry
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UnifiedEntryModal