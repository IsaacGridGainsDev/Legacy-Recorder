#!/usr/bin/env python3
"""
Legacy Recorder Setup Script
Installs dependencies and sets up the application
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    requirements = [
        'customtkinter>=5.2.0',
        'sounddevice>=0.4.6',
        'scipy>=1.10.0',
        'numpy>=1.24.0',
        'APScheduler>=3.10.0',
        'pystray>=0.19.4',
        'Pillow>=9.5.0',
        'pywin32>=306'
    ]
    
    print("🔧 Installing Legacy Recorder dependencies...")
    print("-" * 50)
    
    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
            print(f"✅ {requirement} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {requirement}: {e}")
            return False
    
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows)"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Legacy Recorder.lnk")
        target = sys.executable
        wDir = os.path.dirname(os.path.abspath(__file__))
        arguments = f'"{os.path.join(wDir, "legacy_recorder.py")}"'
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = arguments
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = target
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        return True
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")
        return False

def setup_application_folder():
    """Create application folder structure"""
    app_dir = Path.home() / "LegacyRecorder"
    
    try:
        app_dir.mkdir(exist_ok=True)
        (app_dir / "entries").mkdir(exist_ok=True)
        (app_dir / "config").mkdir(exist_ok=True)
        (app_dir / "assets").mkdir(exist_ok=True)
        
        print(f"✅ Application folder created at: {app_dir}")
        return True
    except Exception as e:
        print(f"❌ Failed to create application folder: {e}")
        return False

def main():
    """Main setup function"""
    print("🌟 Legacy Recorder Setup")
    print("=" * 50)
    print("Setting up Legacy Recorder - Your personal journaling companion")
    print()
    
    # Check Python version
    if sys.version_info < (3.8, 0):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        input("Press Enter to exit...")
        return
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Failed to install some dependencies")
        print("You may need to install them manually using:")
        print("pip install -r requirements.txt")
        input("Press Enter to continue anyway...")
    
    # Setup application folder
    setup_application_folder()
    
    # Try to create desktop shortcut
    create_desktop_shortcut()
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print()
    print("Legacy Recorder is now ready to use.")
    print()
    print("To start the application:")
    print("1. Run: python legacy_recorder.py")
    print("2. Or use the desktop shortcut (if created)")
    print()
    print("Features ready:")
    print("• ✍️  Text journaling with timestamps")
    print("• 🎙️  Audio recording capabilities")
    print("• 📖 Timeline view of all entries")
    print("• 🔍 Search through your entries")
    print("• 📤 Export your data")
    print("• 🔔 Daily reminders (8 AM & 9 PM)")
    print("• 🌙 Dark/Light theme support")
    print("• 🚀 Auto-start with Windows")
    print()
    print("Your legacy recording journey begins now! 🌟")
    
    input("\nPress Enter to exit setup...")

if __name__ == "__main__":
    main()
