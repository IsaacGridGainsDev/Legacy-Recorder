# 🌟 Legacy Recorder

> *Preserve your thoughts, prayers, and wisdom for future generations*

Legacy Recorder is a lightweight, personal journaling application designed to help you document life lessons, experiences, prayers, and reflections. Whether through typed entries or audio recordings, capture your legacy in an organized, searchable format that your children and future generations can treasure.

## ✨ Features

### 📝 **Dual Input Methods**
- **Text Journaling**: Rich text editor with timestamps and tagging
- **Audio Recording**: Simple one-click recording with high-quality audio capture
- **Flexible Tagging**: Organize entries with custom tags (prayer, wisdom, family, lessons)

### 🗂️ **Smart Organization**
- **Chronological Timeline**: View all entries sorted by date
- **Automatic File Structure**: Organized by year/month folders
- **SQLite Database**: Fast, reliable local storage
- **Search Functionality**: Find entries by keywords or tags

### 🔔 **Never Miss a Moment**
- **Daily Reminders**: Customizable notifications at 8 AM and 9 PM
- **System Tray Integration**: Runs quietly in the background
- **Auto-start**: Launches automatically with Windows
- **Persistent Scheduling**: Reminders work even when app is minimized

### 📤 **Export & Backup**
- **TXT Export**: Export entries by month/year as text files
- **DOCX Export**: Professional document format (coming soon)
- **Local File Backup**: Automatic file backups alongside database
- **Data Portability**: Easy to backup and transfer your entire legacy

### 🎨 **Modern Interface**
- **CustomTkinter GUI**: Modern, accessible design
- **Dark/Light Themes**: Eye-friendly viewing options
- **Responsive Layout**: Adapts to different screen sizes
- **Intuitive Navigation**: Easy-to-use sidebar navigation

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11** (Primary support)
- **Python 3.8+** ([Download here](https://python.org))
- **Microphone** (for audio recording)

### Installation Options

#### Option 1: Automated Installation (Recommended)
1. Download all files to a folder
2. Double-click `install.bat`
3. Follow the installation prompts
4. Run `python legacy_recorder.py` to start

#### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create application directory
python setup.py

# Run the application
python legacy_recorder.py
```

## 📁 File Structure

Legacy Recorder creates a well-organized structure in your home directory:

```
📂 LegacyRecorder/
├── 📂 entries/
│   ├── 📂 2025/
│   │   ├── 📂 June/
│   │   │   ├── 📄 18_written.txt
│   │   │   ├── 🎵 18_audio_1687123456.wav
│   │   │   └── 📄 19_written.txt
│   │   └── 📂 July/
│   └── 📂 2024/
├── 📄 legacy.db (SQLite database)
├── 📂 config/
│   └── ⚙️ settings.json
└── 📂 assets/
```

## 🎯 How to Use

### Creating Your First Entry

1. **Launch Legacy Recorder**
   - Run `python legacy_recorder.py`
   - The app will auto-start with Windows after first run

2. **Write a Text Entry**
   - Click "📝 New Entry"
   - Write your thoughts in the text area
   - Add relevant tags (separated by commas)
   - Click "💾 Save Entry"

3. **Record Audio**
   - Click "🎙️ Record Audio"
   - Click "🔴 Start Recording"
   - Speak your thoughts
   - Click "⏹️ Stop Recording"
   - Add tags and save

### Organizing Your Legacy

- **View Timeline**: See all entries in chronological order
- **Search Entries**: Find specific memories by keywords
- **Export Data**: Create backups or share with family
- **Customize Settings**: Adjust reminders, themes, and preferences

## ⚙️ Settings & Customization

### Daily Reminders
- **Morning Reminder**: Default 8:00 AM
- **Evening Reminder**: Default 9:00 PM
- **Custom Times**: Set your preferred reminder schedule
- **Enable/Disable**: Toggle reminders on/off

### Themes & Appearance
- **Dark Mode**: Easy on the eyes for evening journaling
- **Light Mode**: Clean, professional look for day use
- **Font Size**: Adjustable from 10-20pt for accessibility
- **Window Size**: Resizable interface

### Data Management
- **Auto-backup**: Files saved to organized folders
- **Export Options**: TXT format with more formats coming
- **Search Indexing**: Fast full-text search across all entries
- **Tag Organization**: Custom tagging system

## 🔧 Technical Details

### System Requirements
- **OS**: Windows 10/11 (64-bit recommended)
- **RAM**: 150MB or less
- **Storage**: Minimal (grows with your entries)
- **Python**: 3.8+ with pip

### Dependencies
- **CustomTkinter**: Modern GUI framework
- **SoundDevice**: Audio recording capabilities
- **SQLite3**: Local database (built-in)
- **APScheduler**: Background reminder system
- **Pystray**: System tray integration

### Privacy & Security
- **100% Local**: All data stays on your computer
- **No Internet Required**: Works completely offline
- **Encrypted Storage**: Planned for Phase 2
- **Privacy First**: No telemetry or data collection

## 🛠️ Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Audio recording not working**
- Check microphone permissions
- Ensure microphone is not used by other apps
- Try restarting the application

**Reminders not showing**
- Check Windows notification settings
- Ensure app is allowed to run in background
- Verify reminder times in Settings

**Database errors**
- Check folder permissions in LegacyRecorder directory
- Restart application
- Contact support if issues persist

## 🗺️ Roadmap

### Phase 1 (Current) ✅
- [x] Text and audio entry creation
- [x] Timeline view and search
- [x] Daily reminders
- [x] Basic export functionality
- [x] Auto-start integration

### Phase 2 (Planned) 🔄
- [ ] Speech-to-text transcription
- [ ] Enhanced export formats (DOCX, PDF)
- [ ] Local encryption
- [ ] Sentiment analysis and mood tracking
- [ ] Photo attachments

### Phase 3 (Future) 📋
- [ ] Cloud backup options
- [ ] Mobile app companion
- [ ] Family sharing features
- [ ] Advanced search with AI
- [ ] Multi-language support

## 💡 Usage Ideas

### For Parents
- Document parenting lessons learned
- Record bedtime stories for children
- Share family traditions and values
- Preserve childhood memories and milestones

### For Personal Growth
- Daily gratitude entries
- Goal setting and progress tracking
- Reflection on life lessons
- Spiritual and prayer journaling

### For Families
- Family history documentation
- Holiday and tradition recording
- Wisdom from grandparents
- Legacy preservation for future generations

## 🤝 Contributing

Legacy Recorder is designed as a personal tool, but suggestions and improvements are welcome:

1. **Bug Reports**: Describe the issue with steps to reproduce
2. **Feature Requests**: Explain how the feature would help your legacy recording
3. **Code Contributions**: Follow the existing code style and add tests

## 📄 License

This project is open source and available under the MIT License. Feel free to modify and customize for your personal use.

## 🌟 Support

Your legacy matters. If Legacy Recorder helps you preserve precious memories and wisdom for future generations, consider:

- ⭐ Starring this project
- 📢 Sharing with friends and family
- 💬 Providing feedback for improvements

---

**"The best time to plant a tree was 20 years ago. The second best time is now."**

Start recording your legacy today. Your future generations will thank you. 🌱

---

*Built with ❤️ for preserving what matters most*
