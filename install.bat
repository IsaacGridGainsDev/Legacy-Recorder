@echo off
title Legacy Recorder - Installation
color 0B

echo.
echo  =======================================================
echo  🌟 Legacy Recorder - Installation Script
echo  =======================================================
echo.
echo  This will install Legacy Recorder and its dependencies
echo  Your personal journaling companion for preserving
echo  thoughts, prayers, and wisdom for future generations.
echo.

pause

echo.
echo 🔧 Installing Python dependencies...
echo.

REM Install required packages
pip install customtkinter>=5.2.0
pip install sounddevice>=0.4.6
pip install scipy>=1.10.0
pip install numpy>=1.24.0
pip install APScheduler>=3.10.0
pip install pystray>=0.19.4
pip install Pillow>=9.5.0
pip install pywin32>=306

echo.
echo ✅ Dependencies installed!
echo.

REM Create application folder
echo 📁 Setting up application directory...
python -c "
import os
from pathlib import Path
app_dir = Path.home() / 'LegacyRecorder'
app_dir.mkdir(exist_ok=True)
(app_dir / 'entries').mkdir(exist_ok=True)
(app_dir / 'config').mkdir(exist_ok=True)
(app_dir / 'assets').mkdir(exist_ok=True)
print(f'Application folder created at: {app_dir}')
"

echo.
echo 🎉 Installation Complete!
echo.
echo Legacy Recorder is now ready to use.
echo.
echo To start the application:
echo • Run: python legacy_recorder.py
echo • Or double-click the Python file
echo.
echo Features available:
echo • ✍️  Write text entries with rich formatting
echo • 🎙️  Record audio reflections
echo • 📖 View timeline of all your entries
echo • 🔍 Search through your legacy
echo • 📤 Export your data as TXT files
echo • 🔔 Daily reminders at 8 AM and 9 PM
echo • 🌙 Beautiful dark/light themes
echo • 🚀 Auto-start with Windows
echo.
echo Your journey of legacy recording begins now! 🌟
echo.

pause
