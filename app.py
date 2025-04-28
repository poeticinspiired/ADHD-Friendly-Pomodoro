import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import time
import threading
import datetime
from win10toast import ToastNotifier
import winsound
from PIL import Image, ImageTk

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("ADHD-Friendly Pomodoro Timer")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#2E2E2E")
        
        # Set icon (would use a real icon in production)
        # Skip iconbitmap since it can cause issues if no icon is available
        try:
            self.root.iconbitmap(default=self.root.iconbitmap())
        except:
            pass  # Skip if no icon is available
        
        # Initialize toast notifier
        self.toaster = ToastNotifier()
        
        # Default settings
        self.settings = {
            "work_time": 25,
            "short_break": 5,
            "long_break": 15,
            "cycles_before_long_break": 4,
            "sound_enabled": True,
            "notification_enabled": True,
            "warning_time": 1,  # minutes before end to show warning
            "theme": "dark",
            "completed_sessions": 0
        }
        
        # Timer state variables
        self.time_left = self.settings["work_time"] * 60
        self.timer_running = False
        self.timer_paused = False
        self.current_mode = "work"  # "work", "short_break", "long_break"
        self.completed_cycles = 0
        self.warning_shown = False
        self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        
        # Load settings if exist
        self.load_settings()
        
        # Create UI components
        self.create_ui()
        
        # Update timer display
        self.update_timer_display()
        
        # Create a thread for the timer
        self.timer_thread = None

    def load_settings(self):
        """Load settings from JSON file if it exists"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def create_ui(self):
        """Create all UI components"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title label
        title_label = tk.Label(
            self.main_frame, 
            text="ADHD-Friendly Pomodoro", 
            font=("Arial", 24, "bold"),
            fg="#FF6B6B",  # High contrast pinkish-red
            bg="#2E2E2E"
        )
        title_label.pack(pady=(0, 20))
        
        # Mode label (work/break)
        self.mode_label = tk.Label(
            self.main_frame,
            text="WORK TIME",
            font=("Arial", 18),
            fg="#FFFFFF",
            bg="#2E2E2E"
        )
        self.mode_label.pack(pady=(0, 10))
        
        # Timer display
        self.timer_display = tk.Label(
            self.main_frame,
            text="25:00",
            font=("Arial", 72, "bold"),
            fg="#FFFFFF",
            bg="#2E2E2E"
        )
        self.timer_display.pack(pady=(0, 20))
        
        # Progress frame
        progress_frame = tk.Frame(self.main_frame, bg="#2E2E2E")
        progress_frame.pack(fill="x", pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            variable=self.progress_var
        )
        self.progress_bar.pack(pady=10)
        
        # Create a style for buttons
        style = ttk.Style()
        style.configure(
            "TButton",
            font=("Arial", 12, "bold"),
            padding=10
        )
        
        # Control buttons
        controls_frame = tk.Frame(self.main_frame, bg="#2E2E2E")
        controls_frame.pack(pady=10)
        
        self.start_button = ttk.Button(
            controls_frame,
            text="Start",
            command=self.start_timer,
            style="TButton"
        )
        self.start_button.grid(row=0, column=0, padx=10)
        
        self.pause_button = ttk.Button(
            controls_frame,
            text="Pause",
            command=self.pause_timer,
            state="disabled",
            style="TButton"
        )
        self.pause_button.grid(row=0, column=1, padx=10)
        
        self.reset_button = ttk.Button(
            controls_frame,
            text="Reset",
            command=self.reset_timer,
            style="TButton"
        )
        self.reset_button.grid(row=0, column=2, padx=10)
        
        self.skip_button = ttk.Button(
            controls_frame,
            text="Skip",
            command=self.skip_interval,
            style="TButton"
        )
        self.skip_button.grid(row=0, column=3, padx=10)
        
        # Session counter and settings
        bottom_frame = tk.Frame(self.main_frame, bg="#2E2E2E")
        bottom_frame.pack(fill="x", pady=(20, 0), side="bottom")
        
        # Completed sessions
        sessions_frame = tk.Frame(bottom_frame, bg="#2E2E2E")
        sessions_frame.pack(side="left", padx=20)
        
        sessions_label = tk.Label(
            sessions_frame,
            text="Completed sessions:",
            font=("Arial", 12),
            fg="#AAAAAA",
            bg="#2E2E2E"
        )
        sessions_label.pack(side="left")
        
        self.sessions_counter = tk.Label(
            sessions_frame,
            text=str(self.settings["completed_sessions"]),
            font=("Arial", 12, "bold"),
            fg="#FF6B6B",
            bg="#2E2E2E"
        )
        self.sessions_counter.pack(side="left", padx=(5, 0))
        
        # Settings button
        settings_button = ttk.Button(
            bottom_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            style="TButton"
        )
        settings_button.pack(side="right", padx=20)
        
        # Timer interval buttons
        interval_frame = tk.Frame(self.main_frame, bg="#2E2E2E")
        interval_frame.pack(pady=(20, 0))
        
        interval_label = tk.Label(
            interval_frame,
            text="Quick intervals:",
            font=("Arial", 12),
            fg="#AAAAAA",
            bg="#2E2E2E"
        )
        interval_label.grid(row=0, column=0, padx=(0, 10))
        
        intervals = [
            ("15 min", 15),
            ("20 min", 20),
            ("25 min", 25),
            ("30 min", 30)
        ]
        
        for i, (text, mins) in enumerate(intervals):
            btn = ttk.Button(
                interval_frame,
                text=text,
                command=lambda m=mins: self.set_custom_work_time(m),
                style="TButton"
            )
            btn.grid(row=0, column=i+1, padx=5)

    def update_timer_display(self):
        """Update the timer display with current time left"""
        minutes, seconds = divmod(self.time_left, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.timer_display.config(text=time_string)
        
        # Update progress bar
        if self.current_mode == "work":
            total_time = self.settings["work_time"] * 60
        elif self.current_mode == "short_break":
            total_time = self.settings["short_break"] * 60
        else:  # long_break
            total_time = self.settings["long_break"] * 60
        
        progress_value = 100 - (self.time_left / total_time * 100)
        self.progress_var.set(progress_value)
        
        # Update mode label
        if self.current_mode == "work":
            self.mode_label.config(text="WORK TIME", fg="#FF6B6B")
        elif self.current_mode == "short_break":
            self.mode_label.config(text="SHORT BREAK", fg="#4CAF50")
        else:  # long_break
            self.mode_label.config(text="LONG BREAK", fg="#2196F3")

    def timer_function(self):
        """The main timer function that runs in a separate thread"""
        while self.timer_running and not self.timer_paused:
            if self.time_left <= 0:
                self.handle_timer_completion()
                break
            
            # Check if we need to show a warning
            warning_seconds = self.settings["warning_time"] * 60
            if not self.warning_shown and self.time_left <= warning_seconds:
                self.show_warning()
                
            time.sleep(1)
            self.time_left -= 1
            
            # Update UI from the main thread
            self.root.after(0, self.update_timer_display)

    def handle_timer_completion(self):
        """Handle what happens when a timer completes"""
        self.timer_running = False
        
        # Play sound if enabled
        if self.settings["sound_enabled"]:
            winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
        
        # Show notification if enabled
        if self.settings["notification_enabled"]:
            if self.current_mode == "work":
                self.toaster.show_toast(
                    "Work session complete!",
                    "Time to take a break! Great job focusing!",
                    duration=5,
                    threaded=True
                )
            else:
                self.toaster.show_toast(
                    "Break time over!",
                    "Ready to focus again?",
                    duration=5,
                    threaded=True
                )
        
        # Update session counter if work session completed
        if self.current_mode == "work":
            self.settings["completed_sessions"] += 1
            self.sessions_counter.config(text=str(self.settings["completed_sessions"]))
            self.save_settings()
        
        # Move to next interval
        self.move_to_next_interval()
        
        # Update UI
        self.root.after(0, self.update_timer_display)
        self.root.after(0, self.update_button_states)

    def show_warning(self):
        """Show warning notification before timer ends"""
        self.warning_shown = True
        
        if self.settings["notification_enabled"]:
            if self.current_mode == "work":
                self.toaster.show_toast(
                    "Almost done!",
                    f"{self.settings['warning_time']} minute(s) left in work session",
                    duration=3,
                    threaded=True
                )
            else:
                self.toaster.show_toast(
                    "Break ending soon",
                    f"{self.settings['warning_time']} minute(s) left in break",
                    duration=3,
                    threaded=True
                )
        
        if self.settings["sound_enabled"]:
            winsound.Beep(440, 200)  # Gentle beep

    def move_to_next_interval(self):
        """Decide what the next interval should be"""
        if self.current_mode == "work":
            self.completed_cycles += 1
            
            if self.completed_cycles >= self.settings["cycles_before_long_break"]:
                self.current_mode = "long_break"
                self.time_left = self.settings["long_break"] * 60
                self.completed_cycles = 0
            else:
                self.current_mode = "short_break"
                self.time_left = self.settings["short_break"] * 60
        else:
            # If coming from a break, move to work mode
            self.current_mode = "work"
            self.time_left = self.settings["work_time"] * 60
            
        # Reset warning flag for next interval
        self.warning_shown = False

    def start_timer(self):
        """Start or resume the timer"""
        if self.timer_paused:
            # Resume the timer
            self.timer_paused = False
            self.update_button_states()
        else:
            # Start a new timer
            self.timer_running = True
            self.timer_paused = False
            
            # Start a new thread for the timer
            self.timer_thread = threading.Thread(target=self.timer_function)
            self.timer_thread.daemon = True  # Allow the thread to be terminated when the main program exits
            self.timer_thread.start()
            
            # Update button states
            self.update_button_states()
    
    def pause_timer(self):
        """Pause the current timer"""
        if self.timer_running and not self.timer_paused:
            self.timer_paused = True
            self.update_button_states()
    
    def reset_timer(self):
        """Reset the current interval timer"""
        # Stop the timer if it's running
        self.timer_running = False
        self.timer_paused = False
        
        # Reset the time based on current mode
        if self.current_mode == "work":
            self.time_left = self.settings["work_time"] * 60
        elif self.current_mode == "short_break":
            self.time_left = self.settings["short_break"] * 60
        else:  # long_break
            self.time_left = self.settings["long_break"] * 60
            
        # Reset warning flag
        self.warning_shown = False
        
        # Update the display
        self.update_timer_display()
        self.update_button_states()
    
    def skip_interval(self):
        """Skip to the next interval"""
        # Stop the current timer
        self.timer_running = False
        self.timer_paused = False
        
        # Move to the next interval
        self.move_to_next_interval()
        
        # Update the display
        self.update_timer_display()
        self.update_button_states()
    
    def update_button_states(self):
        """Update the states of control buttons based on timer state"""
        if self.timer_running:
            if self.timer_paused:
                self.start_button.config(text="Resume", state="normal")
                self.pause_button.config(state="disabled")
            else:
                self.start_button.config(state="disabled")
                self.pause_button.config(state="normal")
        else:
            self.start_button.config(text="Start", state="normal")
            self.pause_button.config(state="disabled")
    
    def set_custom_work_time(self, minutes):
        """Set a custom work time interval"""
        # Only allow changing if timer is not running
        if not self.timer_running:
            self.settings["work_time"] = minutes
            
            # If in work mode, update the current timer
            if self.current_mode == "work":
                self.time_left = minutes * 60
                self.update_timer_display()
                
            # Show feedback to user
            messagebox.showinfo("Work Time Updated", f"Work interval set to {minutes} minutes")
            
            # Save settings
            self.save_settings()
    
    def open_settings(self):
        """Open the settings dialog"""
        # Create a toplevel window for settings
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Pomodoro Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg="#2E2E2E")
        settings_window.resizable(False, False)
        settings_window.grab_set()  # Make the window modal
        
        # Create a frame for settings
        settings_frame = tk.Frame(settings_window, bg="#2E2E2E")
        settings_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title_label = tk.Label(
            settings_frame,
            text="Timer Settings",
            font=("Arial", 18, "bold"),
            fg="#FF6B6B",
            bg="#2E2E2E"
        )
        title_label.pack(pady=(0, 20))
        
        # Create variables for settings
        work_time_var = tk.IntVar(value=self.settings["work_time"])
        short_break_var = tk.IntVar(value=self.settings["short_break"])
        long_break_var = tk.IntVar(value=self.settings["long_break"])
        cycles_var = tk.IntVar(value=self.settings["cycles_before_long_break"])
        warning_time_var = tk.IntVar(value=self.settings["warning_time"])
        sound_var = tk.BooleanVar(value=self.settings["sound_enabled"])
        notif_var = tk.BooleanVar(value=self.settings["notification_enabled"])
        
        # Create settings controls
        # Work time
        self.create_setting_control(settings_frame, "Work Time (minutes)", work_time_var, 1, 60)
        
        # Short break time
        self.create_setting_control(settings_frame, "Short Break (minutes)", short_break_var, 1, 30)
        
        # Long break time
        self.create_setting_control(settings_frame, "Long Break (minutes)", long_break_var, 5, 60)
        
        # Cycles before long break
        self.create_setting_control(settings_frame, "Work Cycles Before Long Break", cycles_var, 1, 10)
        
        # Warning time
        self.create_setting_control(settings_frame, "Warning Time (minutes before end)", warning_time_var, 0, 5)
        
        # Checkboxes for toggles
        # Sound toggle
        sound_frame = tk.Frame(settings_frame, bg="#2E2E2E")
        sound_frame.pack(fill="x", pady=10)
        
        sound_check = ttk.Checkbutton(
            sound_frame,
            text="Enable Sound Alerts",
            variable=sound_var
        )
        sound_check.pack(side="left")
        
        # Notification toggle
        notif_frame = tk.Frame(settings_frame, bg="#2E2E2E")
        notif_frame.pack(fill="x", pady=10)
        
        notif_check = ttk.Checkbutton(
            notif_frame,
            text="Enable Desktop Notifications",
            variable=notif_var
        )
        notif_check.pack(side="left")
        
        # Reset sessions counter button
        reset_frame = tk.Frame(settings_frame, bg="#2E2E2E")
        reset_frame.pack(fill="x", pady=20)
        
        reset_button = ttk.Button(
            reset_frame,
            text="Reset Completed Sessions Counter",
            command=lambda: self.reset_sessions_counter()
        )
        reset_button.pack()
        
        # Save and cancel buttons
        button_frame = tk.Frame(settings_frame, bg="#2E2E2E")
        button_frame.pack(fill="x", pady=20, side="bottom")
        
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=settings_window.destroy
        )
        cancel_button.pack(side="left", padx=10)
        
        save_button = ttk.Button(
            button_frame,
            text="Save Settings",
            command=lambda: self.save_settings_from_dialog(
                settings_window,
                work_time_var.get(),
                short_break_var.get(),
                long_break_var.get(),
                cycles_var.get(),
                warning_time_var.get(),
                sound_var.get(),
                notif_var.get()
            )
        )
        save_button.pack(side="right", padx=10)
    
    def create_setting_control(self, parent, label_text, variable, min_val, max_val):
        """Helper to create a labeled spinner control for settings"""
        frame = tk.Frame(parent, bg="#2E2E2E")
        frame.pack(fill="x", pady=10)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Arial", 12),
            fg="#FFFFFF",
            bg="#2E2E2E"
        )
        label.pack(side="left")
        
        spinner = ttk.Spinbox(
            frame,
            from_=min_val,
            to=max_val,
            textvariable=variable,
            width=5
        )
        spinner.pack(side="right")
    
    def save_settings_from_dialog(self, window, work, short, long, cycles, warning, sound, notif):
        """Save settings from the dialog values"""
        # Update settings dict
        self.settings["work_time"] = work
        self.settings["short_break"] = short
        self.settings["long_break"] = long
        self.settings["cycles_before_long_break"] = cycles
        self.settings["warning_time"] = warning
        self.settings["sound_enabled"] = sound
        self.settings["notification_enabled"] = notif
        
        # Save to file
        self.save_settings()
        
        # If timer is not running, update time_left to match new settings
        if not self.timer_running:
            if self.current_mode == "work":
                self.time_left = self.settings["work_time"] * 60
            elif self.current_mode == "short_break":
                self.time_left = self.settings["short_break"] * 60
            else:  # long_break
                self.time_left = self.settings["long_break"] * 60
            
            self.update_timer_display()
        
        # Close the window
        window.destroy()
        
        # Show confirmation
        messagebox.showinfo("Settings Saved", "Your settings have been updated")
    
    def reset_sessions_counter(self):
        """Reset the completed sessions counter"""
        self.settings["completed_sessions"] = 0
        self.sessions_counter.config(text="0")
        self.save_settings()
        messagebox.showinfo("Counter Reset", "Completed sessions counter has been reset to 0")

# Main function to start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

