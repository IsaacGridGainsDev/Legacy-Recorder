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
from PIL import Image, ImageDraw, ImageFont # Added ImageFont
import io

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark") # User can toggle this
ctk.set_default_color_theme("blue") 

# Define some theme constants for easier styling
THEME_CORNER_RADIUS = 8
THEME_BUTTON_HEIGHT = 40
THEME_CARD_FG_COLOR_DARK = "#2B2B2B" # Dark theme card (no alpha)
THEME_CARD_FG_COLOR_LIGHT = "#E0E0E0" # Light theme card (no alpha)
THEME_SIDEBAR_FG_COLOR_DARK = "#212121" # Dark theme sidebar (no alpha)
THEME_SIDEBAR_FG_COLOR_LIGHT = "#D6D6D6" # Light theme sidebar (no alpha)


class LegacyRecorder:
    def __init__(self):
        self.app_dir = Path.home() / "LegacyRecorder"
        self.entries_dir = self.app_dir / "entries"
        self.config_dir = self.app_dir / "config"
        self.db_path = self.app_dir / "legacy.db"
        self.settings_path = self.config_dir / "settings.json"
        
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.current_playback_thread = None
        self.is_playing_audio = False
        self.sidebar_visible = False 
        self.currently_playing_file = None 
        self.dashboard_frame_cached = None
        
        self.scheduler = BackgroundScheduler()
        
        self.setup_directories()
        self.setup_database()
        self.load_settings()
        self.setup_gui()
        self.setup_scheduler()
        self.setup_autostart()
        
        try:
            print("Available audio input devices:")
            devices = sd.query_devices()
            input_devices = [device for device in devices if device['max_input_channels'] > 0]
            if not input_devices:
                print("  No input devices found by sounddevice.")
            for i, device in enumerate(input_devices):
                print(f"  {i}: {device['name']} (Input Channels: {device['max_input_channels']})")
            print("-" * 30)
        except Exception as e:
            print(f"Error querying audio devices: {e}")
            
    def setup_directories(self):
        self.app_dir.mkdir(exist_ok=True)
        self.entries_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
        
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().strftime("%B")
        year_dir = self.entries_dir / str(current_year)
        month_dir = year_dir / current_month
        month_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_database(self):
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
        default_settings = {
            "theme": "dark", "reminders_enabled": True,
            "morning_reminder": "08:00", "evening_reminder": "21:00", "font_size": 12
        }
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r') as f:
                    self.settings = {**default_settings, **json.load(f)}
            except: self.settings = default_settings
        else:
            self.settings = default_settings
            self.save_settings()
    
    def save_settings(self):
        with open(self.settings_path, 'w') as f: json.dump(self.settings, f, indent=2)
    
    def setup_gui(self):
        self.root = ctk.CTk()
        self.root.title("Legacy Recorder - Preserve Your Journey")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.root.grid_rowconfigure(0, weight=0) 
        self.root.grid_rowconfigure(1, weight=1) 
        self.root.grid_columnconfigure(0, weight=0) 
        self.root.grid_columnconfigure(1, weight=1) 
        
        self.create_header_frame()
        self.create_sidebar() 
        self.create_main_content_area() 

        self.show_dashboard() 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_header_frame(self):
        self.header_frame = ctk.CTkFrame(self.root, height=40, corner_radius=0, fg_color="transparent") 
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=(5,0)) 

        self.menu_button = ctk.CTkButton(self.header_frame, text="☰", width=40, height=THEME_BUTTON_HEIGHT-10,
                                         corner_radius=THEME_CORNER_RADIUS, command=self.toggle_sidebar)
        self.menu_button.pack(side="left", padx=5, pady=5)

        self.home_button = ctk.CTkButton(self.header_frame, text="🏠", width=40, command=self.show_dashboard)

    def _get_current_card_fg_color(self):
        return THEME_CARD_FG_COLOR_DARK if ctk.get_appearance_mode().lower() == "dark" else THEME_CARD_FG_COLOR_LIGHT

    def _get_current_sidebar_fg_color(self):
        return THEME_SIDEBAR_FG_COLOR_DARK if ctk.get_appearance_mode().lower() == "dark" else THEME_SIDEBAR_FG_COLOR_LIGHT

    def create_sidebar(self):
        sidebar_fg = self._get_current_sidebar_fg_color()
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=THEME_CORNER_RADIUS, fg_color=sidebar_fg)
        self.sidebar.grid_rowconfigure(8, weight=1) 
        
        title_label = ctk.CTkLabel(self.sidebar, text="Legacy Recorder", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.nav_buttons = []
        nav_items = [
            ("📝 New Entry", self.show_new_entry), ("🎙️ Record Audio", self.show_audio_recorder),
            ("📖 View Timeline", self.show_timeline), ("🔍 Search Entries", self.show_search),
            ("📤 Export Data", self.show_export), ("⚙️ Settings", self.show_settings)
        ]
        for i, (text, command) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(self.sidebar, text=text, command=command, width=160, height=THEME_BUTTON_HEIGHT, corner_radius=THEME_CORNER_RADIUS)
            btn.grid(row=i, column=0, padx=20, pady=5)
            self.nav_buttons.append(btn)
        
        self.theme_btn = ctk.CTkButton(self.sidebar, text="🌙 Dark Mode", command=self.toggle_theme, width=160, height=THEME_BUTTON_HEIGHT, corner_radius=THEME_CORNER_RADIUS)
        self.theme_btn.grid(row=7, column=0, padx=20, pady=5)
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=9, column=0, padx=20, pady=(0, 20))

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.main_frame.grid_configure(column=0, columnspan=2) 
            self.root.grid_columnconfigure(0, weight=0) 
        else:
            self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(0,5), pady=(0,5)) 
            self.main_frame.grid_configure(column=1, columnspan=1) 
            self.root.grid_columnconfigure(0, weight=0, minsize=200) 
        self.sidebar_visible = not self.sidebar_visible
    
    def create_main_content_area(self): 
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5) 
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0) 
        self.main_frame.grid_rowconfigure(1, weight=1) 
        self.main_frame.grid_rowconfigure(2, weight=1) 

    def clear_main_frame(self):
        # Ungrid all direct children of main_frame. Destroy those that are not the cached dashboard.
        children_to_destroy = []
        for widget in self.main_frame.winfo_children():
            if widget == self.dashboard_frame_cached:
                widget.grid_remove() # Just ungrid the cached dashboard
            else:
                children_to_destroy.append(widget) # Mark others for destruction
        
        for widget in children_to_destroy:
            widget.destroy()

    def _update_home_button_visibility(self, show_home):
        if show_home:
            self.home_button.pack(side="left", padx=5, pady=5, before=self.menu_button) 
        else:
            self.home_button.pack_forget()
            
    def show_dashboard(self):
        self._update_home_button_visibility(False) 

        if self.dashboard_frame_cached is None:
            self.clear_main_frame() 
            
            self.dashboard_frame_cached = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.dashboard_frame_cached.grid(row=0, column=0, rowspan=3, columnspan=1, sticky="nsew") 
            
            self.dashboard_frame_cached.grid_columnconfigure(0, weight=2) 
            self.dashboard_frame_cached.grid_columnconfigure(1, weight=1) 
            self.dashboard_frame_cached.grid_rowconfigure(0, weight=0)    
            self.dashboard_frame_cached.grid_rowconfigure(1, weight=1)    

            dashboard_header = ctk.CTkLabel(self.dashboard_frame_cached, text="🚀 Dashboard", font=ctk.CTkFont(size=28, weight="bold"))
            dashboard_header.grid(row=0, column=0, columnspan=2, pady=(10,20), padx=20, sticky="w")

            nav_cards_frame = ctk.CTkFrame(self.dashboard_frame_cached, fg_color="transparent")
            nav_cards_frame.grid(row=1, column=0, padx=(20,10), pady=10, sticky="nsew")
            nav_cards_frame.grid_columnconfigure(0, weight=1)
            nav_cards_frame.grid_columnconfigure(1, weight=1) 
            for i in range(3): nav_cards_frame.grid_rowconfigure(i, weight=0) 

            card_items = [
                ("📝 New Text Entry", self.show_new_entry), ("🎙️ Record Audio", self.show_audio_recorder),
                ("📖 View Timeline", self.show_timeline), ("🔍 Search Entries", self.show_search),
                ("⚙️ Settings", self.show_settings), ("📤 Export Data", self.show_export)
            ]
            card_fg_color = self._get_current_card_fg_color()
            for i, (text, command) in enumerate(card_items):
                card_base = ctk.CTkFrame(nav_cards_frame, corner_radius=THEME_CORNER_RADIUS, fg_color=card_fg_color)
                card_base.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
                card_base.grid_rowconfigure(0, weight=1)
                card_base.grid_columnconfigure(0, weight=1)
                
                card_button = ctk.CTkButton(card_base, text=text, command=command, 
                                     height=max(60, THEME_BUTTON_HEIGHT + 20), font=ctk.CTkFont(size=16),
                                     corner_radius=THEME_CORNER_RADIUS-2, fg_color="transparent", hover=True, anchor="center")
                card_button.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

            self.engagement_frame_cached_ref = ctk.CTkFrame(self.dashboard_frame_cached, corner_radius=THEME_CORNER_RADIUS, fg_color=card_fg_color) 
            self.engagement_frame_cached_ref.grid(row=1, column=1, padx=(10,20), pady=10, sticky="nsew")
            self.engagement_frame_cached_ref.grid_columnconfigure(0, weight=1)

            engagement_header = ctk.CTkLabel(self.engagement_frame_cached_ref, text="📊 Engagement", font=ctk.CTkFont(size=18, weight="bold"))
            engagement_header.pack(pady=(10,5), padx=10, anchor="w")
            
            self.stats_labels = {} 
            stats_to_display = {
                "total_entries": "Total Entries: N/A", "text_entries": "Text Entries: N/A",
                "audio_entries": "Audio Entries: N/A", "last_entry_date": "Last Entry: N/A"
            }
            for key, default_text in stats_to_display.items():
                lbl = ctk.CTkLabel(self.engagement_frame_cached_ref, text=default_text, font=ctk.CTkFont(size=12))
                lbl.pack(pady=3, padx=10, anchor="w")
                self.stats_labels[key] = lbl
            
            activity_chart_header = ctk.CTkLabel(self.engagement_frame_cached_ref, text="📈 Recent Activity (7 Days)", font=ctk.CTkFont(size=14, weight="bold"))
            activity_chart_header.pack(pady=(20,5), padx=10, anchor="w")
            self.activity_chart_frame = ctk.CTkFrame(self.engagement_frame_cached_ref, height=100, fg_color="transparent")
            self.activity_chart_frame.pack(fill="x", expand=True, padx=10, pady=5)
            
            self.nav_cards_frame_cached_ref = nav_cards_frame
            # Store reference to engagement frame for theme updates if needed
            self.engagement_frame_dashboard_ref = self.engagement_frame_cached_ref
        
        # Instead of self.clear_main_frame(), manage gridding directly for dashboard
        # Hide other views if any are present (should be handled by clear_main_frame if called from other views)
        for widget in self.main_frame.winfo_children():
            if widget != self.dashboard_frame_cached:
                widget.grid_remove() # Hide non-dashboard elements if any were left

        self.dashboard_frame_cached.grid(row=0, column=0, rowspan=3, columnspan=2, sticky="nsew") # Ensure it spans correctly
        self.load_dashboard_stats()

        if self.sidebar_visible: self.toggle_sidebar()

    def load_dashboard_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM entries")
            self.stats_labels["total_entries"].configure(text=f"Total Entries: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM entries WHERE type='text'")
            self.stats_labels["text_entries"].configure(text=f"Text Entries: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM entries WHERE type='audio'")
            self.stats_labels["audio_entries"].configure(text=f"Audio Entries: {cursor.fetchone()[0]}")
            cursor.execute("SELECT MAX(date) FROM entries")
            last_date = cursor.fetchone()[0]
            self.stats_labels["last_entry_date"].configure(text=f"Last Entry: {datetime.datetime.strptime(last_date, '%Y-%m-%d').strftime('%b %d, %Y') if last_date else 'None'}")

            for widget in self.activity_chart_frame.winfo_children(): widget.destroy() 
            end_date, start_date = datetime.date.today(), datetime.date.today() - datetime.timedelta(days=6)
            activity_data = { (start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d"): 0 for i in range(7) }
            cursor.execute("SELECT date, COUNT(*) FROM entries WHERE date BETWEEN ? AND ? GROUP BY date", (start_date, end_date))
            for date_str, count in cursor.fetchall(): activity_data[date_str] = count
            
            max_val = max(activity_data.values() or [1])
            self.activity_chart_frame.grid_columnconfigure(list(range(7)), weight=1)
            for idx, (date_key, count) in enumerate(sorted(activity_data.items())):
                ratio = count / max_val
                h = int(ratio * 60)
                day_f = ctk.CTkFrame(self.activity_chart_frame, fg_color="transparent")
                day_f.grid(row=0, column=idx, sticky="nsew", padx=1)
                day_f.grid_rowconfigure(0, weight=1); day_f.grid_rowconfigure(1, weight=0); day_f.grid_columnconfigure(0, weight=1)
                bar_c = ctk.ThemeManager.theme["CTkButton"]["fg_color"] if count > 0 else "transparent"
                bar = ctk.CTkFrame(day_f, width=15, height=h, fg_color=bar_c, corner_radius=2)
                bar.grid(row=0, column=0, sticky="s", pady=(max(0, 60-h),0))
                dt = datetime.datetime.strptime(date_key, "%Y-%m-%d")
                date_lbl = ctk.CTkLabel(day_f, text=str(dt.day), font=ctk.CTkFont(size=9))
                date_lbl.grid(row=1, column=0, sticky="n", pady=(2,0))
        except Exception as e: print(f"Error loading dashboard stats: {e}")
        finally: conn.close()
            
    def show_new_entry(self):
        self.clear_main_frame()
        self._update_home_button_visibility(True)
        self.main_frame.grid_rowconfigure(1, weight=0) 
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_rowconfigure(3, weight=0)
        self.main_frame.grid_rowconfigure(4, weight=0)

        header = ctk.CTkLabel(self.main_frame, text="✍️ Create New Entry", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(10,10), padx=20, sticky="w") 
        
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        date_label = ctk.CTkLabel(self.main_frame, text=f"📅 {today}", font=ctk.CTkFont(size=14))
        date_label.grid(row=1, column=0, pady=(0, 20), sticky="w")
        
        self.text_entry = ctk.CTkTextbox(self.main_frame, height=300, font=ctk.CTkFont(size=self.settings["font_size"]))
        self.text_entry.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        self.text_entry.insert("1.0", "Dear Future Generation,\n\nToday I want to share with you...")
        
        tags_frame = ctk.CTkFrame(self.main_frame)
        tags_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        tags_frame.grid_columnconfigure(1, weight=1)
        
        tags_label = ctk.CTkLabel(tags_frame, text="🏷️ Tags:")
        tags_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="prayer, wisdom, family, lesson")
        self.tags_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=15)
        
        save_btn = ctk.CTkButton(self.main_frame, text="💾 Save Entry", command=self.save_text_entry, height=THEME_BUTTON_HEIGHT, corner_radius=THEME_CORNER_RADIUS, font=ctk.CTkFont(size=16, weight="bold"))
        save_btn.grid(row=4, column=0, pady=20)
    
    def show_audio_recorder(self):
        self.clear_main_frame()
        self._update_home_button_visibility(True)
        
        header = ctk.CTkLabel(self.main_frame, text="🎙️ Record Audio Entry", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(10,10), padx=20, sticky="w")
        
        self.recording_status = ctk.CTkLabel(self.main_frame, text="Ready to record", font=ctk.CTkFont(size=16))
        self.recording_status.grid(row=1, column=0, pady=20)
        
        self.record_btn = ctk.CTkButton(self.main_frame, text="🔴 Start Recording", command=self.toggle_recording, height=60, corner_radius=THEME_CORNER_RADIUS, font=ctk.CTkFont(size=18, weight="bold"))
        self.record_btn.grid(row=2, column=0, pady=20)
        
        self.audio_level = ctk.CTkProgressBar(self.main_frame, width=300)
        self.audio_level.grid(row=3, column=0, pady=20)
        self.audio_level.set(0)
        
        tags_frame = ctk.CTkFrame(self.main_frame)
        tags_frame.grid(row=4, column=0, sticky="ew", pady=20, padx=50)
        tags_frame.grid_columnconfigure(1, weight=1)
        
        tags_label = ctk.CTkLabel(tags_frame, text="🏷️ Tags:")
        tags_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.audio_tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="voice, reflection, prayer")
        self.audio_tags_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=15)
    
    def show_timeline(self):
        self.clear_main_frame()
        self._update_home_button_visibility(True)
        
        header = ctk.CTkLabel(self.main_frame, text="📖 Entry Timeline", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(10,0), padx=20, sticky="w")
        
        self.main_frame.grid_columnconfigure(0, weight=1) 
        self.main_frame.grid_rowconfigure(0, weight=0) 
        self.main_frame.grid_rowconfigure(1, weight=0) # Chart container row, fixed height
        self.main_frame.grid_rowconfigure(2, weight=1) # Entries list, expandable

        self.create_timeline_activity_chart() 
        
        # Ensure timeline_frame is created correctly for entries
        self.timeline_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent") 
        self.timeline_frame.grid(row=2, column=0, sticky="nsew", pady=(10,20), padx=20) 
        self.timeline_frame.grid_columnconfigure(0, weight=1) 
        
        self.timeline_play_buttons = {} 
        self.load_timeline_entries() 
    
    def create_timeline_activity_chart(self):
        # This method places its content in self.main_frame at row=1
        chart_container = ctk.CTkFrame(self.main_frame, height=100, fg_color="transparent") # Reduced height for compactness
        chart_container.grid(row=1, column=0, sticky="ew", pady=(5,10), padx=20) # pady adjusted
        chart_container.grid_columnconfigure(0, weight=1)
        chart_container.grid_rowconfigure(0, weight=0) # Title row
        chart_container.grid_rowconfigure(1, weight=1) # Bars row

        chart_title = ctk.CTkLabel(chart_container, text="Activity - Last 30 Days", font=ctk.CTkFont(size=12, weight="bold")) # Smaller title
        chart_title.grid(row=0, column=0, pady=(0,2), sticky="w")

        self.timeline_activity_bars_frame = ctk.CTkFrame(chart_container, fg_color="transparent", height=60) # Reduced height
        self.timeline_activity_bars_frame.grid(row=1, column=0, sticky="nsew")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=29)
            
            activity_data = {}
            current_date_iter = start_date
            while current_date_iter <= end_date:
                activity_data[current_date_iter.strftime("%Y-%m-%d")] = 0
                current_date_iter += datetime.timedelta(days=1)
            
            cursor.execute("SELECT date, COUNT(*) FROM entries WHERE date BETWEEN ? AND ? GROUP BY date", (start_date, end_date))
            
            raw_counts = cursor.fetchall()
            for date_str, count_val in raw_counts: 
                if date_str in activity_data: 
                    activity_data[date_str] = count_val

            max_val = max(activity_data.values() or [1]) # Ensure max_val is at least 1
            
            num_days = len(activity_data)
            
            for widget in self.timeline_activity_bars_frame.winfo_children():
                widget.destroy()

            self.timeline_activity_bars_frame.grid_columnconfigure(list(range(num_days)), weight=1) 
            self.timeline_activity_bars_frame.grid_rowconfigure(0, weight=1) # Bar area
            self.timeline_activity_bars_frame.grid_rowconfigure(1, weight=0) # Label area
            
            sorted_dates_keys = sorted(activity_data.keys())

            for idx, date_key in enumerate(sorted_dates_keys):
                count_val = activity_data[date_key] 
                bar_height_ratio = count_val / max_val if max_val > 0 else 0
                bar_pixel_height = int(bar_height_ratio * 40) # Max bar height of 40px for this chart
                
                day_column_frame = ctk.CTkFrame(self.timeline_activity_bars_frame, fg_color="transparent")
                day_column_frame.grid(row=0, column=idx, sticky="nsew", padx=1) # Use row 0 for the combined bar+label column
                day_column_frame.grid_rowconfigure(0, weight=1) 
                day_column_frame.grid_rowconfigure(1, weight=0) 
                day_column_frame.grid_columnconfigure(0, weight=1)

                # Use a very light gray for zero-count days if theme is light, else transparent
                theme_mode = ctk.get_appearance_mode()
                zero_bar_color = "#F0F0F0" if theme_mode == "Light" else "#303030" # Subtle indication for zero days
                bar_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"] if count_val > 0 else zero_bar_color
                
                current_bar_height = bar_pixel_height if count_val > 0 else 2 # Min height for zero-count bars
                
                bar = ctk.CTkFrame(day_column_frame, width=5, height=current_bar_height, 
                                   fg_color=bar_color, corner_radius=1)
                bar.grid(row=0, column=0, sticky="s", pady=(max(0, 40 - current_bar_height),0)) 
                
                dt_obj = datetime.datetime.strptime(date_key, "%Y-%m-%d")
                # Labeling logic: Show day number. If it's 1st, also show month abbreviation.
                day_label_text = str(dt_obj.day)
                if dt_obj.day == 1:
                    day_label_text = f"{dt_obj.strftime('%b')}\n{dt_obj.day}"
                elif idx == 0 or idx == (num_days - 1) or (idx % 7 == 0 and num_days > 14): # Start, end, or weekly for longer views
                    pass # Just day number is fine
                elif num_days <= 14 and idx % 2 == 0: # More frequent for shorter views
                    pass
                else: # Don't show label for other days to reduce clutter
                    day_label_text = ""
                   
                if day_label_text: # Only create label if there's text
                    date_lbl = ctk.CTkLabel(day_column_frame, text=day_label_text, font=ctk.CTkFont(size=7)) # Smaller font
                    date_lbl.grid(row=1, column=0, sticky="n", pady=(1,0))
        except sqlite3.Error as e:
            print(f"Database error loading timeline activity chart: {e}")
        finally:
            if conn:
                conn.close()

    def show_search(self):
        self.clear_main_frame()
        self._update_home_button_visibility(True)
        
        header = ctk.CTkLabel(self.main_frame, text="🔍 Search Entries", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(10,10), padx=20, sticky="w")
        
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=20)
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(20, 10), pady=15)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter keywords...")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        
        search_btn = ctk.CTkButton(search_frame, text="🔍 Search", command=self.perform_search)
        search_btn.grid(row=0, column=2, padx=(0, 20), pady=15)
        
        self.search_results = ctk.CTkScrollableFrame(self.main_frame, height=300)
        self.search_results.grid(row=2, column=0, sticky="nsew", pady=20)
    
    def show_export(self):
        self.clear_main_frame()
        self._update_home_button_visibility(True)
        
        header = ctk.CTkLabel(self.main_frame, text="📤 Export Data", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(10,10), padx=20, sticky="w")
        
        export_frame = ctk.CTkFrame(self.main_frame)
        export_frame.grid(row=1, column=0, pady=20, padx=50, sticky="ew")
        
        date_label = ctk.CTkLabel(export_frame, text="Export Range:", font=ctk.CTkFont(size=16, weight="bold"))
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
        
        export_txt_btn = ctk.CTkButton(export_frame, text="📄 Export as TXT", command=self.export_txt, height=THEME_BUTTON_HEIGHT, corner_radius=THEME_CORNER_RADIUS)
        export_txt_btn.grid(row=2, column=0, padx=20, pady=20)
        
        export_docx_btn = ctk.CTkButton(export_frame, text="📄 Export as DOCX", command=self.export_docx, height=THEME_BUTTON_HEIGHT, corner_radius=THEME_CORNER_RADIUS)
        export_docx_btn.grid(row=2, column=1, padx=20, pady=20)
    
    def show_settings(self):
        self.clear_main_frame()
        self._update_home_button_visibility(True)
        
        header = ctk.CTkLabel(self.main_frame, text="⚙️ Settings", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, pady=(10,10), padx=20, sticky="w")
        
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.grid(row=1, column=0, pady=20, padx=50, sticky="ew")
        
        reminder_label = ctk.CTkLabel(settings_frame, text="📅 Daily Reminders", font=ctk.CTkFont(size=16, weight="bold"))
        reminder_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="w")
        
        self.reminders_switch = ctk.CTkSwitch(settings_frame, text="Enable reminders")
        self.reminders_switch.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        
        if self.settings["reminders_enabled"]: self.reminders_switch.select()
        
        font_label = ctk.CTkLabel(settings_frame, text="🔤 Font Size:")
        font_label.grid(row=2, column=0, pady=(20, 10), sticky="w")
        
        self.font_slider = ctk.CTkSlider(settings_frame, from_=10, to=20, number_of_steps=10)
        self.font_slider.grid(row=2, column=1, pady=(20, 10), sticky="ew", padx=(20, 0))
        self.font_slider.set(self.settings["font_size"])
        
        save_settings_btn = ctk.CTkButton(settings_frame, text="💾 Save Settings", command=self.save_user_settings, height=THEME_BUTTON_HEIGHT, corner_radius=THEME_CORNER_RADIUS)
        save_settings_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    def save_text_entry(self):
        content = self.text_entry.get("1.0", "end-1c").strip()
        tags = self.tags_entry.get().strip()
        if not content or content == "Dear Future Generation,\n\nToday I want to share with you...":
            messagebox.showwarning("Empty Entry", "Please write something before saving.")
            return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO entries (date, type, content, tags) VALUES (?, ?, ?, ?)", (today, 'text', content, tags))
        conn.commit()
        conn.close()
        self.save_text_to_file(content, today)
        messagebox.showinfo("Success", "Entry saved successfully!")
        self.text_entry.delete("1.0", "end")
        self.tags_entry.delete(0, "end")
        self.update_status("Entry saved")
        if self.dashboard_frame_cached: self.load_dashboard_stats()
    
    def save_text_to_file(self, content, date):
        year, month, day = datetime.datetime.now().year, datetime.datetime.now().strftime("%B"), datetime.datetime.now().day
        month_dir = self.entries_dir / str(year) / month
        month_dir.mkdir(parents=True, exist_ok=True)
        filepath = month_dir / f"{day:02d}_written.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Date: {date}\nType: Text Entry\n{'-'*50}\n{content}")
    
    def toggle_recording(self):
        if not self.is_recording: self.start_recording()
        else: self.stop_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.audio_data = []
        self.record_btn.configure(text="⏹️ Stop Recording")
        self.recording_status.configure(text="🔴 Recording...")
        self.recording_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.recording_thread.start()
        self.update_status("Recording audio...")
    
    def record_audio(self):
        def callback(indata, frames, time_info, status):
            if status: pass
            if self.is_recording:
                self.audio_data.extend(indata.copy())
                rms = np.sqrt(np.mean(indata**2))
                normalized_rms = min(rms * 10, 1.0) 
                self.root.after(0, self.update_audio_level_display, normalized_rms)
        try:
            with sd.InputStream(callback=callback, samplerate=self.sample_rate, channels=1, dtype='float32'):
                while self.is_recording: time.sleep(0.1) 
        except Exception as e:
            print(f"Error during audio recording stream: {e}")
            messagebox.showerror("Audio Error", f"Could not start audio recording: {e}")
            self.is_recording = False 
            self.record_btn.configure(text="🔴 Start Recording")
            self.recording_status.configure(text="Error: Could not record")
    
    def stop_recording(self):
        self.is_recording = False
        self.record_btn.configure(text="🔴 Start Recording")
        self.recording_status.configure(text="Processing...")
        if len(self.audio_data) > 0:
            try: audio_array = np.array(self.audio_data, dtype=np.float32)
            except Exception as e:
                messagebox.showerror("Audio Processing Error", f"Failed to process audio data: {e}")
                self.recording_status.configure(text="Ready to record"); return
            today = datetime.datetime.now()
            month_dir = self.entries_dir / str(today.year) / today.strftime("%B")
            month_dir.mkdir(parents=True, exist_ok=True)
            filepath = month_dir / f"{today.day:02d}_audio_{int(time.time())}.wav"
            try: wav.write(str(filepath), self.sample_rate, audio_array)
            except Exception as e:
                messagebox.showerror("Audio Save Error", f"Failed to save audio file: {e}")
                self.recording_status.configure(text="Ready to record"); return
            self.save_audio_entry(str(filepath), self.audio_tags_entry.get().strip())
            messagebox.showinfo("Success", f"Audio recorded and saved!\nFile: {filepath.name}")
            self.audio_tags_entry.delete(0, "end")
            self.update_status("Audio saved")
            if self.dashboard_frame_cached: self.load_dashboard_stats()
        else: messagebox.showwarning("No Audio", "No audio was recorded.")
        self.recording_status.configure(text="Ready to record")
    
    def save_audio_entry(self, filepath, tags):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO entries (date, type, content, tags) VALUES (?, ?, ?, ?)", (today, 'audio', filepath, tags))
        conn.commit()
        conn.close()
    
    def load_timeline_entries(self):
        for widget in self.timeline_frame.winfo_children(): widget.destroy()
        self.timeline_play_buttons.clear() 
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, type, content, tags, timestamp FROM entries ORDER BY timestamp DESC LIMIT 20") # Added id
        entries = cursor.fetchall()
        conn.close()
        if not entries:
            ctk.CTkLabel(self.timeline_frame, text="No entries yet. Start recording your legacy!", font=ctk.CTkFont(size=16)).grid(row=0, column=0, pady=50, padx=20, sticky="ew")
            return
        for i, (entry_id, date, entry_type, content, tags, timestamp) in enumerate(entries): # Added entry_id
            entry_frame = ctk.CTkFrame(self.timeline_frame, corner_radius=THEME_CORNER_RADIUS-2, fg_color=self._get_current_card_fg_color())
            entry_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=5) 
            entry_frame.grid_columnconfigure(1, weight=1) # Main content
            entry_frame.grid_columnconfigure(2, weight=0) # Button column

            icon = "📝" if entry_type == "text" else "🎙️"
            ctk.CTkLabel(entry_frame, text=icon, font=ctk.CTkFont(size=20)).grid(row=0, column=0, rowspan=3, padx=15, pady=10, sticky="ns")
            
            details_frame = ctk.CTkFrame(entry_frame, fg_color="transparent") 
            details_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=5)
            details_frame.grid_columnconfigure(0, weight=1)
            
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            ctk.CTkLabel(details_frame, text=dt.strftime("%B %d, %Y at %I:%M %p"), font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
            
            preview_content = content
            if entry_type == "text":
                preview_content = (content[:100] + "...") if len(content) > 100 else content
            else: # audio
                preview_content = f"Audio file: {Path(content).name}"
            ctk.CTkLabel(details_frame, text=preview_content, font=ctk.CTkFont(size=11), wraplength=350, anchor="w", justify="left").grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
            
            if tags: ctk.CTkLabel(details_frame, text=f"🏷️ {tags}", font=ctk.CTkFont(size=10), text_color="gray", anchor="w").grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))
            
            action_button_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
            action_button_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="e")

            if entry_type == 'audio':
                btn = ctk.CTkButton(action_button_frame, text="▶️ Play", width=60, height=THEME_BUTTON_HEIGHT-10, corner_radius=THEME_CORNER_RADIUS-2)
                btn.configure(command=lambda c=content, b=btn: self.toggle_audio_playback(c, b))
                btn.pack(pady=2) # Use pack for simple vertical layout
                self.timeline_play_buttons[content] = btn
            elif entry_type == 'text':
                view_btn = ctk.CTkButton(action_button_frame, text="📄 View", width=60, height=THEME_BUTTON_HEIGHT-10, corner_radius=THEME_CORNER_RADIUS-2)
                view_btn.configure(command=lambda current_id=entry_id: self.show_text_entry_dialog(current_id))
                view_btn.pack(pady=2)

    def update_audio_level_display(self, level):
        if hasattr(self, 'audio_level') and self.audio_level.winfo_exists(): self.audio_level.set(level)

    def toggle_audio_playback(self, audio_filepath, button_widget=None): 
        active_play_button = button_widget 
        if self.is_playing_audio and hasattr(self, 'currently_playing_file') and self.currently_playing_file == audio_filepath:
            self.stop_current_audio_playback()
        else:
            self.stop_current_audio_playback() 
            if active_play_button and active_play_button.winfo_exists(): active_play_button.configure(text="⏹️ Stop")
            if hasattr(self, 'timeline_play_buttons'):
                for fp, btn in self.timeline_play_buttons.items():
                    if btn.winfo_exists() and btn != active_play_button: btn.configure(text="▶️ Play")
            self.play_audio_entry(audio_filepath, active_play_button)

    def play_audio_entry(self, audio_filepath, button_widget=None): 
        if not Path(audio_filepath).exists():
            messagebox.showerror("Playback Error", f"Audio file not found: {audio_filepath}", parent=self.root); return
        self.currently_playing_file = audio_filepath 
        def _play():
            self.is_playing_audio = True
            try:
                samplerate, audio_data_arr = wav.read(audio_filepath)
                sd.play(audio_data_arr, samplerate); sd.wait()  
            except Exception as e: messagebox.showerror("Playback Error", f"Could not play audio: {e}", parent=self.root)
            finally:
                self.is_playing_audio = False; self.currently_playing_file = None
                if button_widget and button_widget.winfo_exists(): self.root.after(0, lambda bw=button_widget: bw.configure(text="▶️ Play"))
                self.current_playback_thread = None
        self.current_playback_thread = threading.Thread(target=_play, daemon=True); self.current_playback_thread.start()

    def stop_current_audio_playback(self):
        if self.is_playing_audio:
            sd.stop(); self.is_playing_audio = False
            if hasattr(self, 'timeline_play_buttons'):
                for btn in self.timeline_play_buttons.values():
                    if btn.winfo_exists(): btn.configure(text="▶️ Play")
            self.currently_playing_file = None 

    def perform_search(self):
        query = self.search_entry.get().strip().lower()
        if not query: return
        for widget in self.search_results.winfo_children(): widget.destroy()
        conn = sqlite3.connect(self.db_path); cursor = conn.cursor()
        cursor.execute("SELECT id, date, type, content, tags, timestamp FROM entries WHERE LOWER(content) LIKE ? OR LOWER(tags) LIKE ? ORDER BY timestamp DESC", (f'%{query}%', f'%{query}%')) # Added id
        results = cursor.fetchall(); conn.close()
        if not results: ctk.CTkLabel(self.search_results, text="No matching entries found.").grid(row=0, column=0, pady=20); return
        for i, (entry_id, date, entry_type, content, tags, timestamp) in enumerate(results): # Added entry_id
            result_frame = ctk.CTkFrame(self.search_results, corner_radius=THEME_CORNER_RADIUS-2, fg_color=self._get_current_card_fg_color()) # Use card color
            result_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=10)
            result_frame.grid_columnconfigure(1, weight=1) # Details column
            result_frame.grid_columnconfigure(2, weight=0) # Button column

            icon = "📝" if entry_type == "text" else "🎙️"
            ctk.CTkLabel(result_frame, text=icon, font=ctk.CTkFont(size=18)).grid(row=0, column=0, rowspan=2, padx=10, pady=5, sticky="ns")

            details_inner_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            details_inner_frame.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
            details_inner_frame.grid_columnconfigure(0, weight=1)

            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00')); date_str = dt.strftime("%B %d, %Y")
            ctk.CTkLabel(details_inner_frame, text=f"{date_str}", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w")
            
            preview_content = content
            if entry_type == "text":
                preview_content = (content[:150] + "...") if len(content) > 150 else content
            else: # audio
                preview_content = f"Audio file: {Path(content).name}"
            ctk.CTkLabel(details_inner_frame, text=preview_content, font=ctk.CTkFont(size=11), wraplength=350, anchor="w", justify="left").grid(row=1, column=0, sticky="w")
            if tags: ctk.CTkLabel(details_inner_frame, text=f"🏷️ {tags}", font=ctk.CTkFont(size=10), text_color="gray", anchor="w").grid(row=2, column=0, sticky="w")

            action_button_frame_search = ctk.CTkFrame(result_frame, fg_color="transparent")
            action_button_frame_search.grid(row=0, column=2, rowspan=2, padx=10, pady=5, sticky="e")

            if entry_type == 'text':
                view_btn_search = ctk.CTkButton(action_button_frame_search, text="📄 View", width=60, height=THEME_BUTTON_HEIGHT-10, corner_radius=THEME_CORNER_RADIUS-2)
                view_btn_search.configure(command=lambda current_id=entry_id: self.show_text_entry_dialog(current_id))
                view_btn_search.pack(pady=2)
            elif entry_type == 'audio': # Add play button for audio in search too, for consistency
                play_btn_search = ctk.CTkButton(action_button_frame_search, text="▶️ Play", width=60, height=THEME_BUTTON_HEIGHT-10, corner_radius=THEME_CORNER_RADIUS-2)
                # Need to ensure self.timeline_play_buttons is managed or a separate dict for search play buttons
                # For simplicity, reusing toggle_audio_playback, but it might need adjustment if state is tied to timeline_play_buttons
                play_btn_search.configure(command=lambda c=content, b=play_btn_search: self.toggle_audio_playback(c, b))
                play_btn_search.pack(pady=2)
                # If managing play button states for search results is needed, a similar dict to self.timeline_play_buttons would be required.
                # For now, this provides the button; state management for play/stop text might need more if many audio results are played.

    def show_text_entry_dialog(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT date, content, tags, timestamp FROM entries WHERE id = ?", (entry_id,))
            entry_data = cursor.fetchone()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not fetch entry: {e}", parent=self.root)
            return
        finally:
            conn.close()

        if not entry_data:
            messagebox.showerror("Error", "Entry not found.", parent=self.root)
            return

        _date_str, content, tags, timestamp_str = entry_data
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.attributes("-topmost", True) # Keep dialog on top
        dialog.title("View Text Entry")
        dialog.geometry("500x400") # Decent default size
        dialog.minsize(400, 300)

        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(2, weight=1) # Textbox row

        dt_object = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        formatted_date = dt_object.strftime("%A, %B %d, %Y at %I:%M %p")
        
        date_label = ctk.CTkLabel(dialog, text=f"📅 {formatted_date}", font=ctk.CTkFont(size=14, weight="bold"))
        date_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        if tags:
            tags_label = ctk.CTkLabel(dialog, text=f"🏷️ Tags: {tags}", font=ctk.CTkFont(size=12))
            tags_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        text_content_box = ctk.CTkTextbox(dialog, font=ctk.CTkFont(size=self.settings.get("font_size", 12)), wrap="word")
        text_content_box.grid(row=2, column=0, padx=15, pady=(0,10), sticky="nsew")
        text_content_box.insert("1.0", content)
        text_content_box.configure(state="disabled") # Make read-only

        close_button = ctk.CTkButton(dialog, text="Close", command=dialog.destroy, height=THEME_BUTTON_HEIGHT-10, corner_radius=THEME_CORNER_RADIUS-2)
        close_button.grid(row=3, column=0, padx=15, pady=10)
        
        dialog.transient(self.root) # Set dialog to be transient to the main window
        dialog.grab_set() # Make dialog modal
        self.root.wait_window(dialog) # Wait for dialog to close

    def export_txt(self):
        year, month = self.year_combo.get(), self.month_combo.get()
        conn = sqlite3.connect(self.db_path); cursor = conn.cursor()
        query_str = "SELECT date, type, content, tags, timestamp FROM entries WHERE date LIKE ? ORDER BY timestamp"
        params = (f'{year}%',)
        if month != "All":
            month_num = datetime.datetime.strptime(month, "%B").month
            params = (f'{year}-{month_num:02d}%',)
        cursor.execute(query_str, params)
        entries = cursor.fetchall(); conn.close()
        if not entries: messagebox.showinfo("No Data", "No entries found for the selected period."); return
        export_content = f"Legacy Recorder Export\nPeriod: {month} {year}\nGenerated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{'='*50}\n\n"
        for date, entry_type, content, tags, timestamp in entries:
            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            export_content += f"Date: {dt.strftime('%B %d, %Y at %I:%M %p')}\nType: {'Text Entry' if entry_type == 'text' else 'Audio Entry'}\n"
            if tags: export_content += f"Tags: {tags}\n"
            export_content += f"{'-'*30}\n{content if entry_type == 'text' else f'Audio file: {Path(content).name}'}\n\n{'='*50}\n\n"
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], initialname=f"legacy_export_{year}_{month}_{int(time.time())}.txt")
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f: f.write(export_content)
            messagebox.showinfo("Export Complete", f"Entries exported to:\n{filepath}")
    
    def export_docx(self): messagebox.showinfo("Feature Coming Soon", "DOCX export will be available in the next update.\nFor now, use TXT export.")
    
    def save_user_settings(self):
        self.settings["reminders_enabled"] = self.reminders_switch.get()
        self.settings["font_size"] = int(self.font_slider.get())
        self.save_settings()
        messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
        self.setup_scheduler()
    
    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode().lower()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.settings["theme"] = new_mode
        self.theme_btn.configure(text="🌞 Light Mode" if new_mode == "light" else "🌙 Dark Mode")
        self.save_settings()
        
        self.sidebar.configure(fg_color=self._get_current_sidebar_fg_color())
        if self.dashboard_frame_cached: 
            card_fg = self._get_current_card_fg_color()
            if hasattr(self, 'nav_cards_frame_cached_ref'): 
                 for child in self.nav_cards_frame_cached_ref.winfo_children(): # Iterate through actual card bases
                    if isinstance(child, ctk.CTkFrame): 
                        child.configure(fg_color=card_fg)
            
            if hasattr(self, 'engagement_frame_dashboard_ref'): # Use stored ref
                 self.engagement_frame_dashboard_ref.configure(fg_color=card_fg)

            self.load_dashboard_stats() 
        
        if hasattr(self, 'timeline_frame') and self.timeline_frame.winfo_exists(): 
            self.create_timeline_activity_chart() # Recreate for theme
            self.load_timeline_entries() # Re-style entries

    def setup_scheduler(self):
        if hasattr(self, 'scheduler') and self.scheduler.running: self.scheduler.shutdown()
        if not self.settings["reminders_enabled"]: return
        self.scheduler = BackgroundScheduler()
        m_time, e_time = self.settings["morning_reminder"].split(":"), self.settings["evening_reminder"].split(":")
        self.scheduler.add_job(self.show_reminder, CronTrigger(hour=int(m_time[0]), minute=int(m_time[1])), args=["Good morning! Time to record your thoughts and reflections."], id="morning_reminder")
        self.scheduler.add_job(self.show_reminder, CronTrigger(hour=int(e_time[0]), minute=int(e_time[1])), args=["Good evening! Take a moment to reflect on your day."], id="evening_reminder")
        self.scheduler.start()
    
    def show_reminder(self, message):
        def show_notification():
            try: font = ImageFont.truetype("arial.ttf", 20) 
            except IOError: font = ImageFont.load_default()
            image = Image.new('RGB', (64, 64), color='blue'); draw = ImageDraw.Draw(image)
            draw.text((10, 20), "LR", fill='white', font=font) # Adjusted text position
            menu = pystray.Menu(pystray.MenuItem("Open Legacy Recorder", self.bring_to_front), pystray.MenuItem("Dismiss", lambda: None))
            icon = pystray.Icon("Legacy Recorder", image, menu=menu)
            icon.notify(message, "Legacy Recorder Reminder")
        if self.root.winfo_viewable(): messagebox.showinfo("Reminder", message)
        else: threading.Thread(target=show_notification, daemon=True).start()
    
    def bring_to_front(self):
        self.root.deiconify(); self.root.lift(); self.root.focus_force()
    
    def setup_autostart(self):
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else f'python "{os.path.abspath(__file__)}"'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "LegacyRecorder", 0, winreg.REG_SZ, exe_path); winreg.CloseKey(key)
        except Exception: pass
    
    def update_status(self, message):
        self.status_label.configure(text=message)
        self.root.after(3000, lambda: self.status_label.configure(text="Ready"))
    
    def on_closing(self):
        if hasattr(self, 'scheduler') and self.scheduler.running: self.scheduler.shutdown()
        result = messagebox.askyesnocancel("Legacy Recorder", "Minimize to system tray to keep reminders active?\n\nYes = Minimize | No = Close | Cancel = Stay", parent=self.root )
        if result is True: self.root.withdraw(); self.create_system_tray()
        elif result is False: self.stop_current_audio_playback(); self.root.destroy()
    
    def create_system_tray(self):
        def create_tray():
            try: font = ImageFont.truetype("arial.ttf", 30) 
            except IOError: font = ImageFont.load_default()
            image = Image.new('RGB', (64, 64), color='blue'); draw = ImageDraw.Draw(image)
            bbox = draw.textbbox((0,0), "LR", font=font); w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((64-w)/2, (64-h)/2), "LR", fill='white', font=font)
            menu = pystray.Menu(
                pystray.MenuItem("Open", self.bring_to_front),
                pystray.MenuItem("New Entry", lambda: self.bring_to_front_and_show('entry')),
                pystray.MenuItem("Record Audio", lambda: self.bring_to_front_and_show('audio')),
                pystray.MenuItem("Quit", self.quit_from_tray)
            )
            self.tray_icon = pystray.Icon("Legacy Recorder", image, "Legacy Recorder", menu)
            self.tray_icon.run()
        threading.Thread(target=create_tray, daemon=True).start()
    
    def bring_to_front_and_show(self, view):
        self.bring_to_front()
        if view == 'entry': self.show_new_entry()
        elif view == 'audio': self.show_audio_recorder()
    
    def quit_from_tray(self):
        self.stop_current_audio_playback() 
        if hasattr(self, 'tray_icon') and self.tray_icon: self.tray_icon.stop()
        if hasattr(self, 'scheduler') and self.scheduler.running: self.scheduler.shutdown()
        self.root.destroy() # Changed from self.root.quit() for cleaner exit
    
    def run(self): self.root.mainloop()

def check_requirements():
    required = ['customtkinter', 'sounddevice', 'scipy', 'numpy', 'apscheduler', 'pystray', 'pillow']
    missing = []
    for pkg in required:
        try: __import__('PIL' if pkg == 'pillow' else pkg)
        except ImportError: missing.append(pkg)
    if missing:
        print(f"Missing required packages: {', '.join(missing)}\nInstall with: pip install {' '.join(missing)}")
        return False
    return True

def main():
    if not check_requirements(): input("Press Enter to exit..."); return
    try: app = LegacyRecorder(); app.run()
    except Exception as e: messagebox.showerror("Error", f"An error occurred: {str(e)}"); print(f"Error: {e}")

if __name__ == "__main__":
    main()
