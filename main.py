#!/usr/bin/env python3
"""
Legacy Recorder - A Personal Journaling App
Purpose: Record or write daily legacy entries for future generations
Author: Generated for Legacy Preservation
"""

import customtkinter as ctk
import sqlite3
import os
import json
import datetime
import threading
import time
import winreg
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pystray
from PIL import Image, ImageDraw
import io

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LegacyRecorder:
    def __init__(self):
        self.app_dir = Path.home() / "LegacyRecorder"
        self.entries_dir = self.app_dir / "entries"
        self.config_dir = self.app_dir / "config"
        self.db_path = self.app_dir / "legacy.db"
        self.settings_path = self.config_dir / "settings.json"
        
        # Audio recording variables
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        
        # Scheduler for reminders
        self.scheduler = BackgroundScheduler()
        
        # Initialize app
        self.setup_directories()
        self.setup_database()
        self.load_settings()
        self.setup_gui()
        self.setup_scheduler()
        self.setup_autostart()
        
    def setup_directories(self):
        """Create necessary directories"""
        self.app_dir.mkdir(exist_ok=True)
        self.entries_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        # Create year/month directories
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().strftime("%B")
        year_dir = self.entries_dir / str(current_year)
        month_dir = year_dir / current_month
        month_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT CHECK(type IN ('text', 'audio')) NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_settings(self):
        """Load app settings"""
        default_settings = {
            "theme": "dark",
            "reminders_enabled": True,
            "morning_reminder": "08:00",
            "evening_reminder": "21:00",
            "font_size": 12
        }
        
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r') as f:
                    self.settings = {**default_settings, **json.load(f)}
            except:
                self.settings = default_settings
        else:
            self.settings = default_settings
            self.save_settings()
    
    def save_settings(self):
        """Save app settings"""
        with open(self.settings_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def setup_gui(self):
        """Initialize the main GUI"""
        self.root = ctk.CTk()
        self.root.title("Legacy Recorder - Preserve Your Journey")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure grid
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create main frames
        self.create_sidebar()
        self.create_main_content()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_sidebar(self):
        """Create sidebar with navigation"""
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(self.sidebar, text="Legacy Recorder", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("📝 New Entry", self.show_new_entry),
            ("🎙️ Record Audio", self.show_audio_recorder),
            ("📖 View Timeline", self.show_timeline),
            ("🔍 Search Entries", self.show_search),
            ("📤 Export Data", self.show_export),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for i, (text, command) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(self.sidebar, text=text, command=command,
                               width=160, height=35)
            btn.grid(row=i, column=0, padx=20, pady=5)
            self.nav_buttons.append(btn)
        
        # Theme toggle
        self.theme_btn = ctk.CTkButton(self.sidebar, text="🌙 Dark Mode", 
                                      command=self.toggle_theme, width=160, height=35)
        self.theme_btn.grid(row=7, column=0, padx=20, pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.sidebar, text="Ready", 
                                        font=ctk.CTkFont(size=12))
        self.status_label.grid(row=9, column=0, padx=20, pady=(0, 20))
    
    def create_main_content(self):
        """Create main content area"""
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Default view - New Entry
        self.show_new_entry()
    
    def clear_main_frame(self):
        """Clear main content area"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_new_entry(self):
        """Show new text entry interface"""
        self.clear_main_frame()
        
        # Header
        header = ctk.CTkLabel(self.main_frame, text="✍️ Create New Entry", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(20, 10), sticky="w")
        
        # Date display
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        date_label = ctk.CTkLabel(self.main_frame, text=f"📅 {today}", 
                                 font=ctk.CTkFont(size=14))
        date_label.grid(row=1, column=0, pady=(0, 20), sticky="w")
        
        # Text entry area
        self.text_entry = ctk.CTkTextbox(self.main_frame, height=300, 
                                        font=ctk.CTkFont(size=self.settings["font_size"]))
        self.text_entry.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        self.text_entry.insert("1.0", "Dear Future Generation,\n\nToday I want to share with you...")
        
        # Tags entry
        tags_frame = ctk.CTkFrame(self.main_frame)
        tags_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        tags_frame.grid_columnconfigure(1, weight=1)
        
        tags_label = ctk.CTkLabel(tags_frame, text="🏷️ Tags:")
        tags_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="prayer, wisdom, family, lesson")
        self.tags_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=15)
        
        # Save button
        save_btn = ctk.CTkButton(self.main_frame, text="💾 Save Entry", 
                                command=self.save_text_entry, height=40,
                                font=ctk.CTkFont(size=16, weight="bold"))
        save_btn.grid(row=4, column=0, pady=20)
    
    def show_audio_recorder(self):
        """Show audio recording interface"""
        self.clear_main_frame()
        
        # Header
        header = ctk.CTkLabel(self.main_frame, text="🎙️ Record Audio Entry", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(20, 10))
        
        # Recording status
        self.recording_status = ctk.CTkLabel(self.main_frame, text="Ready to record", 
                                           font=ctk.CTkFont(size=16))
        self.recording_status.grid(row=1, column=0, pady=20)
        
        # Record button
        self.record_btn = ctk.CTkButton(self.main_frame, text="🔴 Start Recording", 
                                       command=self.toggle_recording, height=60,
                                       font=ctk.CTkFont(size=18, weight="bold"))
        self.record_btn.grid(row=2, column=0, pady=20)
        
        # Audio level indicator (placeholder)
        self.audio_level = ctk.CTkProgressBar(self.main_frame, width=300)
        self.audio_level.grid(row=3, column=0, pady=20)
        self.audio_level.set(0)
        
        # Tags for audio entry
        tags_frame = ctk.CTkFrame(self.main_frame)
        tags_frame.grid(row=4, column=0, sticky="ew", pady=20, padx=50)
        tags_frame.grid_columnconfigure(1, weight=1)
        
        tags_label = ctk.CTkLabel(tags_frame, text="🏷️ Tags:")
        tags_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.audio_tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="voice, reflection, prayer")
        self.audio_tags_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=15)
    
    def show_timeline(self):
        """Show timeline of entries"""
        self.clear_main_frame()
        
        # Header
        header = ctk.CTkLabel(self.main_frame, text="📖 Entry Timeline", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(20, 10), sticky="w")
        
        # Timeline scrollable frame
        self.timeline_frame = ctk.CTkScrollableFrame(self.main_frame, height=400)
        self.timeline_frame.grid(row=1, column=0, sticky="nsew", pady=20)
        self.timeline_frame.grid_columnconfigure(0, weight=1)
        
        self.load_timeline_entries()
    
    def show_search(self):
        """Show search interface"""
        self.clear_main_frame()
        
        # Header
        header = ctk.CTkLabel(self.main_frame, text="🔍 Search Entries", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(20, 10), sticky="w")
        
        # Search frame
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=20)
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter keywords...")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        
        search_btn = ctk.CTkButton(search_frame, text="🔍 Search", command=self.perform_search)
        search_btn.grid(row=0, column=2, padx=(0, 20), pady=15)
        
        # Results frame
        self.search_results = ctk.CTkScrollableFrame(self.main_frame, height=300)
        self.search_results.grid(row=2, column=0, sticky="nsew", pady=20)
    
    def show_export(self):
        """Show export interface"""
        self.clear_main_frame()
        
        # Header
        header = ctk.CTkLabel(self.main_frame, text="📤 Export Data", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(20, 10), sticky="w")
        
        # Export options
        export_frame = ctk.CTkFrame(self.main_frame)
        export_frame.grid(row=1, column=0, pady=20, padx=50, sticky="ew")
        
        # Date range selection
        date_label = ctk.CTkLabel(export_frame, text="Export Range:", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        date_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))
        
        current_year = datetime.datetime.now().year
        years = [str(year) for year in range(current_year-2, current_year+1)]
        
        self.year_combo = ctk.CTkComboBox(export_frame, values=years, width=120)
        self.year_combo.grid(row=1, column=0, padx=20, pady=10)
        self.year_combo.set(str(current_year))
        
        months = ["All", "January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        self.month_combo = ctk.CTkComboBox(export_frame, values=months, width=120)
        self.month_combo.grid(row=1, column=1, padx=20, pady=10)
        self.month_combo.set("All")
        
        # Export buttons
        export_txt_btn = ctk.CTkButton(export_frame, text="📄 Export as TXT", 
                                      command=self.export_txt, height=40)
        export_txt_btn.grid(row=2, column=0, padx=20, pady=20)
        
        export_docx_btn = ctk.CTkButton(export_frame, text="📄 Export as DOCX", 
                                       command=self.export_docx, height=40)
        export_docx_btn.grid(row=2, column=1, padx=20, pady=20)
    
    def show_settings(self):
        """Show settings interface"""
        self.clear_main_frame()
        
        # Header
        header = ctk.CTkLabel(self.main_frame, text="⚙️ Settings", 
                             font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(20, 10), sticky="w")
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.grid(row=1, column=0, pady=20, padx=50, sticky="ew")
        
        # Reminders section
        reminder_label = ctk.CTkLabel(settings_frame, text="📅 Daily Reminders", 
                                     font=ctk.CTkFont(size=16, weight="bold"))
        reminder_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="w")
        
        self.reminders_switch = ctk.CTkSwitch(settings_frame, text="Enable reminders")
        self.reminders_switch.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        
        if self.settings["reminders_enabled"]:
            self.reminders_switch.select()
        
        # Font size
        font_label = ctk.CTkLabel(settings_frame, text="🔤 Font Size:")
        font_label.grid(row=2, column=0, pady=(20, 10), sticky="w")
        
        self.font_slider = ctk.CTkSlider(settings_frame, from_=10, to=20, number_of_steps=10)
        self.font_slider.grid(row=2, column=1, pady=(20, 10), sticky="ew", padx=(20, 0))
        self.font_slider.set(self.settings["font_size"])
        
        # Save settings button
        save_settings_btn = ctk.CTkButton(settings_frame, text="💾 Save Settings", 
                                         command=self.save_user_settings, height=40)
        save_settings_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    def save_text_entry(self):
        """Save text entry to database"""
        content = self.text_entry.get("1.0", "end-1c").strip()
        tags = self.tags_entry.get().strip()
        
        if not content or content == "Dear Future Generation,\n\nToday I want to share with you...":
            messagebox.showwarning("Empty Entry", "Please write something before saving.")
            return
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT INTO entries (date, type, content, tags)
            VALUES (?, ?, ?, ?)
        ''', (today, 'text', content, tags))
        
        conn.commit()
        conn.close()
        
        # Save to file as backup
        self.save_text_to_file(content, today)
        
        messagebox.showinfo("Success", "Entry saved successfully!")
        self.text_entry.delete("1.0", "end")
        self.tags_entry.delete(0, "end")
        self.update_status("Entry saved")
    
    def save_text_to_file(self, content, date):
        """Save text entry to file"""
        year = datetime.datetime.now().year
        month = datetime.datetime.now().strftime("%B")
        day = datetime.datetime.now().day
        
        year_dir = self.entries_dir / str(year)
        month_dir = year_dir / month
        month_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{day:02d}_written.txt"
        filepath = month_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Date: {date}\n")
            f.write(f"Type: Text Entry\n")
            f.write("-" * 50 + "\n")
            f.write(content)
    
    def toggle_recording(self):
        """Toggle audio recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start audio recording"""
        self.is_recording = True
        self.audio_data = []
        self.record_btn.configure(text="⏹️ Stop Recording")
        self.recording_status.configure(text="🔴 Recording...")
        
        # Start recording in separate thread
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        self.update_status("Recording audio...")
    
    def record_audio(self):
        """Record audio data"""
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_data.extend(indata.copy())
        
        with sd.InputStream(callback=callback, samplerate=self.sample_rate, channels=1):
            while self.is_recording:
                time.sleep(0.1)
    
    def stop_recording(self):
        """Stop audio recording and save"""
        self.is_recording = False
        self.record_btn.configure(text="🔴 Start Recording")
        self.recording_status.configure(text="Processing...")
        
        if len(self.audio_data) > 0:
            # Convert to numpy array
            audio_array = np.array(self.audio_data)
            
            # Save audio file
            today = datetime.datetime.now()
            year = today.year
            month = today.strftime("%B")
            day = today.day
            
            year_dir = self.entries_dir / str(year)
            month_dir = year_dir / month
            month_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{day:02d}_audio_{int(time.time())}.wav"
            filepath = month_dir / filename
            
            # Save as WAV file
            wav.write(str(filepath), self.sample_rate, audio_array)
            
            # Save to database
            tags = self.audio_tags_entry.get().strip()
            self.save_audio_entry(str(filepath), tags)
            
            messagebox.showinfo("Success", f"Audio recorded and saved!\nFile: {filename}")
            self.audio_tags_entry.delete(0, "end")
            self.update_status("Audio saved")
        else:
            messagebox.showwarning("No Audio", "No audio was recorded.")
        
        self.recording_status.configure(text="Ready to record")
    
    def save_audio_entry(self, filepath, tags):
        """Save audio entry to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute('''
            INSERT INTO entries (date, type, content, tags)
            VALUES (?, ?, ?, ?)
        ''', (today, 'audio', filepath, tags))
        
        conn.commit()
        conn.close()
    
    def load_timeline_entries(self):
        """Load and display timeline entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, type, content, tags, timestamp
            FROM entries
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        
        entries = cursor.fetchall()
        conn.close()
        
        if not entries:
            no_entries_label = ctk.CTkLabel(self.timeline_frame, 
                                          text="No entries yet. Start recording your legacy!",
                                          font=ctk.CTkFont(size=16))
            no_entries_label.grid(row=0, column=0, pady=50)
            return
        
        for i, (date, entry_type, content, tags, timestamp) in enumerate(entries):
            entry_frame = ctk.CTkFrame(self.timeline_frame)
            entry_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=10)
            entry_frame.grid_columnconfigure(1, weight=1)
            
            # Entry type icon
            icon = "📝" if entry_type == "text" else "🎙️"
            type_label = ctk.CTkLabel(entry_frame, text=icon, font=ctk.CTkFont(size=20))
            type_label.grid(row=0, column=0, padx=15, pady=10)
            
            # Entry details
            details_frame = ctk.CTkFrame(entry_frame)
            details_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=5)
            details_frame.grid_columnconfigure(0, weight=1)
            
            # Date and time
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime("%B %d, %Y at %I:%M %p")
            date_label = ctk.CTkLabel(details_frame, text=date_str, 
                                    font=ctk.CTkFont(size=12, weight="bold"))
            date_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
            
            # Content preview
            if entry_type == "text":
                preview = content[:100] + "..." if len(content) > 100 else content
            else:
                preview = f"Audio file: {Path(content).name}"
            
            content_label = ctk.CTkLabel(details_frame, text=preview, 
                                       font=ctk.CTkFont(size=11), wraplength=400)
            content_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
            
            # Tags
            if tags:
                tags_label = ctk.CTkLabel(details_frame, text=f"🏷️ {tags}", 
                                        font=ctk.CTkFont(size=10), text_color="gray")
                tags_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))
    
    def perform_search(self):
        """Search entries"""
        query = self.search_entry.get().strip().lower()
        if not query:
            return
        
        # Clear previous results
        for widget in self.search_results.winfo_children():
            widget.destroy()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, type, content, tags, timestamp
            FROM entries
            WHERE LOWER(content) LIKE ? OR LOWER(tags) LIKE ?
            ORDER BY timestamp DESC
        ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            no_results = ctk.CTkLabel(self.search_results, text="No matching entries found.")
            no_results.grid(row=0, column=0, pady=20)
            return
        
        for i, (date, entry_type, content, tags, timestamp) in enumerate(results):
            result_frame = ctk.CTkFrame(self.search_results)
            result_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=10)
            result_frame.grid_columnconfigure(0, weight=1)
            
            # Result content (similar to timeline)
            icon = "📝" if entry_type == "text" else "🎙️"
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = dt.strftime("%B %d, %Y")
            
            header_label = ctk.CTkLabel(result_frame, text=f"{icon} {date_str}", 
                                      font=ctk.CTkFont(size=12, weight="bold"))
            header_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
            
            if entry_type == "text":
                preview = content[:150] + "..." if len(content) > 150 else content
            else:
                preview = f"Audio file: {Path(content).name}"
            
            content_label = ctk.CTkLabel(result_frame, text=preview, 
                                       font=ctk.CTkFont(size=11), wraplength=400)
            content_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
    
    def export_txt(self):
        """Export entries as TXT file"""
        year = self.year_combo.get()
        month = self.month_combo.get()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if month == "All":
            cursor.execute('''
                SELECT date, type, content, tags, timestamp
                FROM entries
                WHERE date LIKE ?
                ORDER BY timestamp
            ''', (f'{year}%',))
        else:
            month_num = datetime.datetime.strptime(month, "%B").month
            cursor.execute('''
                SELECT date, type, content, tags, timestamp
                FROM entries
                WHERE date LIKE ?
                ORDER BY timestamp
            ''', (f'{year}-{month_num:02d}%',))
        
        entries = cursor.fetchall()
        conn.close()
        
        if not entries:
            messagebox.showinfo("No Data", "No entries found for the selected period.")
            return
        
        # Generate export content
        export_content = f"Legacy Recorder Export\n"
        export_content += f"Period: {month} {year}\n"
        export_content += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_content += "=" * 50 + "\n\n"
        
        for date, entry_type, content, tags, timestamp in entries:
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            export_content += f"Date: {dt.strftime('%B %d, %Y at %I:%M %p')}\n"
            export_content += f"Type: {'Text Entry' if entry_type == 'text' else 'Audio Entry'}\n"
            if tags:
                export_content += f"Tags: {tags}\n"
            export_content += "-" * 30 + "\n"
            
            if entry_type == "text":
                export_content += content + "\n"
            else:
                export_content += f"Audio file: {Path(content).name}\n"
            
            export_content += "\n" + "=" * 50 + "\n\n"
        
        # Save file
        filename = f"legacy_export_{year}_{month}_{int(time.time())}.txt"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialname=filename
        )
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(export_content)
            messagebox.showinfo("Export Complete", f"Entries exported to:\n{filepath}")
    
    def export_docx(self):
        """Export entries as DOCX file (placeholder - requires python-docx)"""
        messagebox.showinfo("Feature Coming Soon", 
                          "DOCX export will be available in the next update.\n"
                          "For now, use TXT export.")
    
    def save_user_settings(self):
        """Save user settings"""
        self.settings["reminders_enabled"] = self.reminders_switch.get()
        self.settings["font_size"] = int(self.font_slider.get())
        
        self.save_settings()
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
        
        # Restart scheduler if needed
        self.setup_scheduler()
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        if self.settings["theme"] == "dark":
            ctk.set_appearance_mode("light")
            self.settings["theme"] = "light"
            self.theme_btn.configure(text="🌞 Light Mode")
        else:
            ctk.set_appearance_mode("dark")
            self.settings["theme"] = "dark"
            self.theme_btn.configure(text="🌙 Dark Mode")
        
        self.save_settings()
    
    def setup_scheduler(self):
        """Set up reminder scheduler"""
        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.shutdown()
        
        if not self.settings["reminders_enabled"]:
            return
        
        self.scheduler = BackgroundScheduler()
        
        # Morning reminder
        morning_time = self.settings["morning_reminder"].split(":")
        self.scheduler.add_job(
            self.show_reminder,
            CronTrigger(hour=int(morning_time[0]), minute=int(morning_time[1])),
            args=["Good morning! Time to record your thoughts and reflections."],
            id="morning_reminder"
        )
        
        # Evening reminder
        evening_time = self.settings["evening_reminder"].split(":")
        self.scheduler.add_job(
            self.show_reminder,
            CronTrigger(hour=int(evening_time[0]), minute=int(evening_time[1])),
            args=["Good evening! Take a moment to reflect on your day."],
            id="evening_reminder"
        )
        
        self.scheduler.start()
    
    def show_reminder(self, message):
        """Show reminder notification"""
        # Create system tray notification
        def show_notification():
            # Create a simple icon
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.text((10, 25), "LR", fill='white')
            
            menu = pystray.Menu(
                pystray.MenuItem("Open Legacy Recorder", self.bring_to_front),
                pystray.MenuItem("Dismiss", lambda: None)
            )
            
            icon = pystray.Icon("Legacy Recorder", image, menu=menu)
            icon.notify(message, "Legacy Recorder Reminder")
            
        # Also show in-app notification if window is visible
        if self.root.winfo_viewable():
            messagebox.showinfo("Reminder", message)
        else:
            # Show system notification
            threading.Thread(target=show_notification, daemon=True).start()
    
    def bring_to_front(self):
        """Bring application window to front"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def setup_autostart(self):
        """Set up Windows autostart"""
        try:
            # Get current executable path
            if getattr(sys, 'frozen', False):
                # If running as compiled executable
                exe_path = sys.executable
            else:
                # If running as Python script
                exe_path = f'python "{os.path.abspath(__file__)}"'
            
            # Add to Windows startup registry
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "LegacyRecorder", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            
        except Exception as e:
            # Silently fail if can't set autostart
            pass
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.configure(text=message)
        # Clear status after 3 seconds
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def on_closing(self):
        """Handle application closing"""
        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.shutdown()
        
        # Ask if user wants to minimize to tray instead of closing
        result = messagebox.askyesnocancel(
            "Legacy Recorder", 
            "Would you like to minimize to system tray to keep reminders active?\n\n"
            "Yes = Minimize to tray\n"
            "No = Close completely\n"
            "Cancel = Stay open"
        )
        
        if result is True:
            # Minimize to tray
            self.root.withdraw()
            self.create_system_tray()
        elif result is False:
            # Close completely
            self.root.destroy()
        # If Cancel (None), do nothing - stay open
    
    def create_system_tray(self):
        """Create system tray icon"""
        def create_tray():
            # Create icon
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.text((5, 20), "LR", fill='white', font_size=20)
            
            menu = pystray.Menu(
                pystray.MenuItem("Open Legacy Recorder", self.bring_to_front),
                pystray.MenuItem("New Entry", lambda: self.bring_to_front_and_show('entry')),
                pystray.MenuItem("Record Audio", lambda: self.bring_to_front_and_show('audio')),
                pystray.MenuItem("Quit", self.quit_from_tray)
            )
            
            self.tray_icon = pystray.Icon("Legacy Recorder", image, 
                                        "Legacy Recorder - Recording your legacy", menu)
            self.tray_icon.run()
        
        threading.Thread(target=create_tray, daemon=True).start()
    
    def bring_to_front_and_show(self, view):
        """Bring to front and show specific view"""
        self.bring_to_front()
        if view == 'entry':
            self.show_new_entry()
        elif view == 'audio':
            self.show_audio_recorder()
    
    def quit_from_tray(self):
        """Quit application from system tray"""
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        if hasattr(self, 'scheduler') and self.scheduler.running:
            self.scheduler.shutdown()
        self.root.quit()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Additional utility functions and requirements check
def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'customtkinter', 'sounddevice', 'scipy', 'numpy', 
        'apscheduler', 'pystray', 'pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        return False
    return True

def main():
    """Main application entry point"""
    if not check_requirements():
        input("Press Enter to exit...")
        return
    
    try:
        app = LegacyRecorder()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
