import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
from keyboard import KeyboardFrame
from phrases_window import PhrasesWindow
import logging
import time
import unicodedata

# Placeholder for VoiceSettingsWindow
class VoiceSettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Voice Settings")
        self.window.geometry("400x300")
        self.window.configure(bg="#2A2A2A")
        self.window.transient(parent)
        self.window.grab_set()

        self.tts_engine = pyttsx3.init()
        self.voices = self.tts_engine.getProperty('voices')
        self.selected_voice_index = 0

        tk.Label(self.window, text="Select Voice:", font=("Segoe UI", 12), fg="white", bg="#2A2A2A").pack(pady=10)
        self.voice_var = tk.StringVar()
        voice_names = [voice.name for voice in self.voices]
        self.voice_dropdown = ttk.Combobox(self.window, textvariable=self.voice_var, values=voice_names, state="readonly")
        self.voice_dropdown.current(0)
        self.voice_dropdown.pack(pady=5)

        tk.Button(self.window, text="Test Voice", font=("Segoe UI", 12), fg="white", bg="#2196F3",
                  activebackground="#1976D2", relief="raised", command=self.test_voice).pack(pady=5)

        tk.Button(self.window, text="Save Voice", font=("Segoe UI", 12), fg="white", bg="#4CAF50",
                  activebackground="#45A049", relief="raised", command=self.save_voice).pack(pady=5)

        tk.Button(self.window, text="Close", font=("Segoe UI", 12), fg="white", bg="#F44336",
                  activebackground="#D32F2F", relief="raised", command=self.window.destroy).pack(pady=5)

        logging.info("Voice settings window opened")

    def test_voice(self):
        try:
            selected_index = self.voice_dropdown.current()
            self.tts_engine.setProperty('voice', self.voices[selected_index].id)
            self.tts_engine.say("This is a test of the selected voice.")
            self.tts_engine.runAndWait()
            logging.info(f"Tested voice: {self.voices[selected_index].name}")
        except Exception as e:
            logging.error(f"Error testing voice: {str(e)}")
            messagebox.showerror("Error", f"Failed to test voice: {str(e)}")

    def save_voice(self):
        self.selected_voice_index = self.voice_dropdown.current()
        messagebox.showinfo("Success", "Voice saved successfully!")
        logging.info(f"Saved voice: {self.voices[self.selected_voice_index].name}")

    def get_selected_voice(self):
        return self.selected_voice_index

class UIManager:
    def __init__(self, root, on_calibrate_callback, show_debug_callback):
        self.root = root
        self.on_calibrate_callback = on_calibrate_callback
        self.show_debug_callback = show_debug_callback
        self.shift = False
        self.caps_lock = False
        self.paused = False
        self.pause_btn = None
        self.last_pause_action_time = 0
        self.debounce_delay = 0.5
        self.phrases_window = None
        self.settings_frame = None
        self.dwell_canvas_frame = None
        self.dwell_canvas_visible = False
        self.voice_settings_window = None
        self.tts_engine = pyttsx3.init()
        self.voices = self.tts_engine.getProperty('voices')
        self.current_voice_index = 0
        self.word_list = self.load_word_list()
        self.init_ui()

    def load_word_list(self):
        """Load words from google-10000-english.txt for predictive text."""
        try:
            with open('final/google-10000-english.txt', 'r', encoding='utf-8') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Error loading word list: {str(e)}")
            return ["sup", "sushi", "sun", "suspect", "sus", "suit", "superb"]

    def init_ui(self):
        """Initialize the UI components."""
        logging.info("Initializing UI components")
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_frame()
        self.setup_topbar()
        self.setup_input_controls()
        self.setup_keyboard_area()

        self.debug_button = tk.Button(
            self.sidebar,
            text="🐛\nDebug",
            font=("Segoe UI", 10),
            fg="white",
            bg="#1E1E1E",
            activebackground="#333333",
            activeforeground="white",
            relief="flat",
            command=self.show_debug_callback
        )
        self.debug_button.grid(row=9, column=0, sticky="ew", padx=5, pady=3)

        self.root.bind_all("<Key>", self.on_key_press)

    def setup_sidebar(self):
        """Set up the sidebar with navigation buttons."""
        self.sidebar = tk.Frame(self.root, bg="#1E1E1E", width=120)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(10, weight=1)

        nav_buttons = [
            ("← Back", "←"), ("🔥 QuickFires", "🔥"), ("💬 Phrases", "💬"),
            ("⌨ Keyboard", "⌨"), ("📝 Notes", "📝"), ("⏱ Dashboard", "⏱"),
            ("⏸ Pause Access", "⏸"), ("🛠 Calibrate", "🛠"), ("⚙ Settings", "⚙")
        ]
        self.nav_button_widgets = {}
        for i, (text, icon) in enumerate(nav_buttons):
            if "Pause Access" in text:
                btn = tk.Button(
                    self.sidebar, text=f"{icon}\n{text.split()[1]}", font=("Segoe UI", 11),
                    fg="white", bg="#1E1E1E", activebackground="#333333",
                    activeforeground="white", relief="flat", wraplength=140, justify="center",
                    height=3
                )
                self.pause_btn = btn
                btn.configure(command=lambda t=text: self.sidebar_action(t))
                logging.debug(f"Pause button created: {self.pause_btn}")
            else:
                btn = tk.Button(
                    self.sidebar, text=f"{icon}\n{text.split()[1]}", font=("Segoe UI", 11),
                    fg="white", bg="#1E1E1E", activebackground="#333333",
                    activeforeground="white", relief="flat", wraplength=140, justify="center",
                    height=3, command=lambda t=text: self.sidebar_action(t)
                )
            btn.grid(row=i, column=0, sticky="ew", padx=5, pady=3)
            self.nav_button_widgets[text] = btn

    def setup_main_frame(self):
        """Set up the main frame that holds other UI elements."""
        self.main_frame = tk.Frame(self.root, bg="#2A2A2A")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)
        self.main_frame.grid_rowconfigure(1, weight=0)
        self.main_frame.grid_rowconfigure(2, weight=1)

    def setup_topbar(self):
        """Set up the top bar with icons and search entry."""
        self.topbar = tk.Frame(self.main_frame, bg="#3A3A3A", height=40)
        self.topbar.grid(row=0, column=0, sticky="ew", pady=(0,5))
        self.topbar.grid_columnconfigure(4, weight=1)

        top_left_icons = [
            ("←", self.action_back), ("🏠", self.action_home),
            ("⏱", self.action_dashboard), ("🔍", self.action_search)
        ]
        for i, (icon, cmd) in enumerate(top_left_icons):
            tk.Button(
                self.topbar, text=icon, font=("Segoe UI", 14), fg="white", bg="#3A3A3A",
                activebackground="#555555", activeforeground="white", relief="flat",
                command=cmd, width=3, height=1
            ).grid(row=0, column=i, padx=2, pady=2)

        self.title_label = tk.Label(
            self.topbar, text="Keyboard - QWERTY",
            font=("Segoe UI Semibold", 12), fg="white", bg="#3A3A3A"
        )
        self.title_label.grid(row=0, column=4, sticky="ew")

        self.search_var = tk.StringVar(value="Sus")
        self.search_entry = tk.Entry(
            self.topbar, textvariable=self.search_var, font=("Segoe UI", 10),
            width=15, bg="#D1D1D1", fg="black", relief="flat", justify="center"
        )
        self.search_entry.grid(row=0, column=5, padx=5, pady=5)

        top_right_icons = [("💡", self.action_light), ("☁", self.action_cloud),
                           ("🎨", self.action_paint)]
        for i, (icon, cmd) in enumerate(top_right_icons):
            tk.Button(
                self.topbar, text=icon, font=("Segoe UI", 14), fg="white", bg="#3A3A3A",
                activebackground="#555555", activeforeground="white", relief="flat",
                command=cmd, width=3, height=1
            ).grid(row=0, column=6+i, padx=2, pady=2)

    def setup_input_controls(self):
        """Set up the input area with speak button, main input, and action buttons."""
        self.input_controls = tk.Frame(self.main_frame, bg="#4A4A4A", height=60)
        self.input_controls.grid(row=1, column=0, sticky="ew", pady=(0,5))
        self.input_controls.grid_columnconfigure(1, weight=1)

        self.speak_btn = tk.Button(
            self.input_controls, text="💬\nSpeak", font=("Segoe UI", 10),
            fg="white", bg="#3A3A3A", activebackground="#555555", activeforeground="white",
            relief="flat", width=7, height=3, justify="center", command=self.speak_text
        )
        self.speak_btn.grid(row=0, column=0, sticky="nsw", padx=3, pady=3)

        self.main_input_var = tk.StringVar(value="Sus")
        self.main_input = tk.Entry(
            self.input_controls, textvariable=self.main_input_var, font=("Segoe UI", 18),
            bg="white", fg="black", relief="flat", justify="left"
        )
        self.main_input.grid(row=0, column=1, sticky="ew", padx=3, pady=10)
        self.main_input_var.trace_add("write", lambda *args: self.update_suggestions())

        right_btn_texts = [("≡ X\nClear", self.action_clear),
                           ("Abc X\nDelete", self.action_delete),
                           ("↗\nShare", self.action_share)]
        for i, (text, cmd) in enumerate(right_btn_texts):
            tk.Button(
                self.input_controls, text=text, font=("Segoe UI", 9), fg="white",
                bg="#3A3A3A", activebackground="#555555", activeforeground="white",
                relief="flat", width=8, height=3, justify="center", command=cmd
            ).grid(row=0, column=2+i, sticky="ns", padx=2, pady=3)

    def setup_keyboard_area(self):
        """Set up the keyboard area with suggestions and virtual keyboard."""
        self.keyboard_container = tk.Frame(self.main_frame, bg="#BFC7CE")
        self.keyboard_container.grid(row=2, column=0, sticky="nsew", pady=5)
        self.keyboard_container.grid_columnconfigure(0, weight=1)
        self.keyboard_container.grid_rowconfigure(0, weight=0)
        self.keyboard_container.grid_rowconfigure(1, weight=1)

        self.suggestions_frame = tk.Frame(self.keyboard_container, bg="#D9E6F2", height=50)
        self.suggestions_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.suggestions_frame.grid_columnconfigure((0,1,2,3,4), weight=1)
        self.suggestion_buttons = []
        self.update_suggestions()

        self.keys_frame = KeyboardFrame(
            self.keyboard_container,
            insert_key_callback=self.insert_key,
            toggle_shift_callback=self.toggle_shift,
            toggle_caps_callback=self.toggle_caps,
            update_predictive_text_callback=self.update_suggestions
        )
        self.keys_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def toggle_shift(self):
        """Toggle the shift state and update the keyboard."""
        self.shift = not self.shift
        if self.keys_frame:
            self.keys_frame.create_keyboard()
        logging.debug(f"Shift state toggled: {self.shift}")

    def toggle_caps(self):
        """Toggle the caps lock state and update the keyboard."""
        self.caps_lock = not self.caps_lock
        if self.keys_frame:
            self.keys_frame.create_keyboard()
        logging.debug(f"Caps lock state toggled: {self.caps_lock}")

    def update_suggestions(self):
        """Update suggestion buttons based on the current input text."""
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        current = self.main_input_var.get().lower()
        suggestions = [word for word in self.word_list if word.startswith(current)]
        for i, word in enumerate(suggestions[:5]):
            b = tk.Button(self.suggestions_frame, text=word, font=("Segoe UI", 12),
                          bg="#D9E6F2", fg="#1A1A1A", relief="raised", borderwidth=1,
                          command=lambda w=word: self.insert_suggestion(w))
            b.grid(row=0, column=i, sticky="ew", padx=3, pady=3)

    def reset_ui(self):
        """Reset the UI by hiding all major frames and windows."""
        logging.debug("Resetting UI")
        self.hide_topbar_and_keyboard()
        self.hide_settings()
        self.close_phrases_window()
        # Clear all widgets from main_frame
        for widget in self.main_frame.winfo_children():
            widget.grid_remove()
            logging.debug(f"Removed widget from main_frame: {widget}")
        if hasattr(self.root, 'calibration_window') and self.root.calibration_window.winfo_exists():
            self.root.calibration_window.withdraw()
            logging.debug("Calibration window hidden")

    def show_keyboard_area(self):
        """Show the keyboard area by managing visibility of UI components."""
        self.reset_ui()
        # Check and reinitialize widgets if they don't exist
        if not hasattr(self, 'topbar') or not self.topbar.winfo_exists():
            logging.warning("Topbar missing or destroyed, reinitializing")
            self.setup_topbar()
        if not hasattr(self, 'input_controls') or not self.input_controls.winfo_exists():
            logging.warning("Input controls missing or destroyed, reinitializing")
            self.setup_input_controls()
        if not hasattr(self, 'keyboard_container') or not self.keyboard_container.winfo_exists():
            logging.warning("Keyboard container missing or destroyed, reinitializing")
            self.setup_keyboard_area()
        # Grid keyboard widgets
        self.topbar.grid(row=0, column=0, sticky="ew", pady=(0,5))
        self.input_controls.grid(row=1, column=0, sticky="ew", pady=(0,5))
        self.keyboard_container.grid(row=2, column=0, sticky="nsew", pady=5)
        self.main_input.focus_set()
        logging.debug(f"Main frame children after gridding: {self.main_frame.winfo_children()}")
        logging.info("Keyboard area displayed")

    def hide_topbar_and_keyboard(self):
        """Hide the top bar, input controls, and keyboard frame."""
        if hasattr(self, 'topbar') and self.topbar.winfo_exists():
            self.topbar.grid_remove()
            logging.debug("Top bar hidden")
        if hasattr(self, 'input_controls') and self.input_controls.winfo_exists():
            self.input_controls.grid_remove()
            logging.debug("Input controls hidden")
        if hasattr(self, 'keyboard_container') and self.keyboard_container.winfo_exists():
            self.keyboard_container.grid_remove()
            logging.debug("Keyboard frame hidden")

    def show_settings(self):
        """Show the settings interface."""
        self.reset_ui()
        self.settings_frame = tk.Frame(self.main_frame, bg="#2A2A2A")
        self.settings_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=5, pady=5)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(0, weight=0)
        self.settings_frame.grid_rowconfigure(1, weight=0)
        self.settings_frame.grid_rowconfigure(2, weight=0)
        self.settings_frame.grid_rowconfigure(3, weight=1)

        tk.Label(
            self.settings_frame, text="Settings", font=("Segoe UI", 16, "bold"),
            fg="white", bg="#2A2A2A"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        tk.Button(
            self.settings_frame, text="Dwell Time Settings", font=("Segoe UI", 12),
            fg="white", bg="#2196F3", activebackground="#1976D2",
            relief="raised", command=self.toggle_dwell_canvas
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        tk.Button(
            self.settings_frame, text="Voice Settings", font=("Segoe UI", 12),
            fg="white", bg="#2196F3", activebackground="#1976D2",
            relief="raised", command=self.show_voice_settings
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        tk.Label(
            self.settings_frame, text="More settings coming soon...", font=("Segoe UI", 12),
            fg="gray", bg="#2A2A2A"
        ).grid(row=3, column=0, padx=10, pady=5, sticky="nw")

        logging.info("Settings interface displayed")

    def toggle_dwell_canvas(self):
        """Toggle the visibility of the dwell time settings canvas."""
        if self.dwell_canvas_visible:
            self.hide_dwell_canvas()
        else:
            self.show_dwell_canvas()
        self.dwell_canvas_visible = not self.dwell_canvas_visible

    def show_dwell_canvas(self):
        """Show the dwell time settings canvas."""
        if self.dwell_canvas_frame and self.dwell_canvas_frame.winfo_exists():
            self.dwell_canvas_frame.grid()
            logging.info("Dwell time settings canvas shown")
            return

        self.dwell_canvas_frame = tk.Frame(self.settings_frame, bg="#2A2A2A")
        self.dwell_canvas_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        back_frame = tk.Frame(self.dwell_canvas_frame, bg="#2A2A2A")
        back_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Button(
            back_frame, text="← Back", font=("Segoe UI", 12),
            fg="white", bg="#2196F3", activebackground="#1976D2",
            relief="raised", command=self.toggle_dwell_canvas
        ).grid(row=0, column=0, padx=5, pady=5)

        dwell_frame = tk.Frame(self.dwell_canvas_frame, bg="#2A2A2A")
        dwell_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        tk.Label(
            dwell_frame, text="Dwell Time (seconds):", font=("Segoe UI", 12),
            fg="white", bg="#2A2A2A"
        ).grid(row=0, column=0, padx=5, pady=5)

        self.dwell_entry = tk.Entry(dwell_frame, font=("Segoe UI", 12), width=10)
        self.dwell_entry.insert(0, str(self.root.gaze_tracker.dwell_timer.dwell_time))
        self.dwell_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            dwell_frame, text="Apply", font=("Segoe UI", 12),
            fg="white", bg="#4CAF50", activebackground="#45A049",
            relief="raised", command=lambda: self.update_dwell_time(self.dwell_entry.get())
        ).grid(row=0, column=2, padx=5, pady=5)

        preset_frame = tk.Frame(self.dwell_canvas_frame, bg="#2A2A2A")
        preset_frame.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        tk.Label(
            preset_frame, text="Quick Presets:", font=("Segoe UI", 12),
            fg="white", bg="#2A2A2A"
        ).grid(row=0, column=0, padx=5, pady=5)

        preset_times = [0.5, 1.0, 1.5, 2.0]
        for i, preset in enumerate(preset_times, start=1):
            tk.Button(
                preset_frame, text=f"{preset}s", font=("Segoe UI", 12),
                fg="white", bg="#2196F3", activebackground="#1976D2",
                relief="raised", width=6,
                command=lambda p=preset: self.set_dwell_time_preset(p)
            ).grid(row=0, column=i, padx=5, pady=5)

        logging.info("Dwell time settings canvas created and shown")

    def hide_dwell_canvas(self):
        """Hide the dwell time settings canvas."""
        if self.dwell_canvas_frame and self.dwell_canvas_frame.winfo_exists():
            self.dwell_canvas_frame.grid_remove()
            logging.info("Dwell time settings canvas hidden")

    def show_voice_settings(self):
        """Show the VoiceSettingsWindow."""
        if self.voice_settings_window is None or not self.voice_settings_window.window.winfo_exists():
            self.voice_settings_window = VoiceSettingsWindow(self.root)
            self.voice_settings_window.window.protocol("WM_DELETE_WINDOW", self.on_voice_settings_close)
            logging.info("Voice settings window opened")
        else:
            self.voice_settings_window.window.lift()
            logging.info("Voice settings window brought to front")

    def on_voice_settings_close(self):
        """Handle VoiceSettingsWindow closure and update the voice."""
        if self.voice_settings_window and self.voice_settings_window.window.winfo_exists():
            selected_voice_index = self.voice_settings_window.get_selected_voice()
            if selected_voice_index >= 0:
                self.current_voice_index = selected_voice_index
                logging.info(f"Voice updated to index {self.current_voice_index} on VoiceSettingsWindow close")
            self.voice_settings_window.window.destroy()
        self.voice_settings_window = None

    def hide_settings(self):
        """Hide the settings frame if it exists."""
        if self.dwell_canvas_frame and self.dwell_canvas_frame.winfo_exists():
            self.dwell_canvas_frame.grid_remove()
            self.dwell_canvas_frame = None
            self.dwell_canvas_visible = False
            logging.debug("Dwell canvas hidden")
        if self.voice_settings_window and self.voice_settings_window.window.winfo_exists():
            self.on_voice_settings_close()
        if self.settings_frame and self.settings_frame.winfo_exists():
            self.settings_frame.grid_remove()
            logging.info("Settings frame hidden")
        self.settings_frame = None

    def update_dwell_time(self, value):
        """Update the dwell time in GazeTracker."""
        try:
            new_dwell = float(value)
            self.root.gaze_tracker.dwell_timer.set_dwell_time(new_dwell)
            messagebox.showinfo("Success", f"Dwell time updated to {new_dwell} seconds.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            logging.warning(f"Invalid dwell time value: {e}")

    def set_dwell_time_preset(self, preset):
        """Set the dwell time to a preset value and update the entry field."""
        try:
            self.root.gaze_tracker.dwell_timer.set_dwell_time(preset)
            self.dwell_entry.delete(0, tk.END)
            self.dwell_entry.insert(0, str(preset))
            messagebox.showinfo("Success", f"Dwell time set to {preset} seconds.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            logging.warning(f"Failed to set preset dwell time: {e}")

    def show_phrases_window(self):
        """Show the PhrasesWindow."""
        logging.info("Attempting to show PhrasesWindow")
        try:
            self.reset_ui()
            if self.phrases_window is None or not self.phrases_window.frame.winfo_exists():
                self.phrases_window = PhrasesWindow(self.root, self.main_input_var)
                self.phrases_window.frame.grid(row=0, column=0, sticky="nsew", in_=self.main_frame)  # Grid in main_frame
                logging.info("Phrases window created and gridded")
            else:
                self.phrases_window.frame.grid(row=0, column=0, sticky="nsew", in_=self.main_frame)
                self.phrases_window.frame.lift()
                logging.info("Phrases window brought to front")
        except Exception as e:
            logging.error(f"Error showing PhrasesWindow: {str(e)}")
            messagebox.showerror("Error", f"Failed to show Phrases window: {str(e)}")

    def show_notes(self):
        """Placeholder for Notes section."""
        self.reset_ui()
        self.notes_frame = tk.Frame(self.main_frame, bg="#2A2A2A")
        self.notes_frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(self.notes_frame, text="Notes Section (Not Implemented)", font=("Segoe UI", 16), fg="white", bg="#2A2A2A").grid(row=0, column=0)
        logging.info("Notes section displayed")

    def show_dashboard(self):
        """Placeholder for Dashboard section."""
        self.reset_ui()
        self.dashboard_frame = tk.Frame(self.main_frame, bg="#2A2A2A")
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        tk.Label(self.dashboard_frame, text="Dashboard Section (Not Implemented)", font=("Segoe UI", 16), fg="white", bg="#2A2A2A").grid(row=0, column=0)
        logging.info("Dashboard section displayed")

    def speak_text(self):
        """Speak the text in the main input using text-to-speech."""
        try:
            text = self.main_input_var.get()
            if not text:
                return
            self.tts_engine.setProperty('voice', self.voices[self.current_voice_index].id)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logging.info(f"Text spoken with voice index {self.current_voice_index}: {text}")
        except Exception as e:
            logging.error(f"Error in speak_text: {str(e)}")
            messagebox.showerror("Error", f"Failed to speak text: {str(e)}")

    def insert_suggestion(self, word):
        """Insert a suggestion into the main input."""
        self.main_input_var.set(word)
        logging.debug(f"Suggestion inserted: {word}")

    def on_key_press(self, event):
        """Handle key press events for input."""
        if self.paused:
          logging.debug("Key press ignored due to paused state")
        return
        self.main_input.focus_set()  # Ensure main_input has focus
        logging.debug(f"Key pressed: char='{event.char}', keysym='{event.keysym}'")
        if event.char.isprintable():
         self.insert_key(event.char)
         logging.debug(f"Key inserted: '{event.char}'")
        elif event.keysym == "BackSpace":
         self.action_delete()
         logging.debug("Backspace key pressed")
        elif event.keysym == "Left":
         self.insert_key("LEFT")
         logging.debug("Physical left arrow key pressed")
        elif event.keysym == "Right":
         self.insert_key("RIGHT")
         logging.debug("Physical right arrow key pressed")

    def insert_key(self, key):
       """Insert a key into the main input, respecting shift and caps lock."""
       if self.paused:
        logging.debug("Key insertion ignored due to paused state")
        return
       self.main_input.focus_set()  # Ensure main_input has focus
       current_pos = self.main_input.index(tk.INSERT)  # Get current cursor position
       current_text = self.main_input_var.get()
       logging.debug(f"Current cursor position: {current_pos}, text: '{current_text}'")

       if key == "BACKSPACE":
          self.action_delete()
       elif key == "LEFT":
        if current_pos > 0:
            self.main_input.icursor(current_pos - 1)  # Move cursor left
        logging.debug(f"Cursor moved left to position: {self.main_input.index(tk.INSERT)}")
       elif key == "RIGHT":
        if current_pos < len(current_text):
            self.main_input.icursor(current_pos + 1)  # Move cursor right
        logging.debug(f"Cursor moved right to position: {self.main_input.index(tk.INSERT)}")
       else:
        if self.shift or self.caps_lock:
            key = key.upper()
        # Insert key at current cursor position
        new_text = current_text[:current_pos] + key + current_text[current_pos:]
        self.main_input_var.set(new_text)
        self.main_input.icursor(current_pos + 1)  # Move cursor after inserted key
        if self.shift:
            self.shift = False
        logging.debug(f"Inserted key: '{key}', new text: '{new_text}', cursor at: {self.main_input.index(tk.INSERT)}")

    def sidebar_action(self, text):
        """Handle sidebar button actions."""
        if isinstance(text, str):
            text = unicodedata.normalize('NFKC', text)
        logging.debug(f"Sidebar action triggered: {text}")

        current_time = time.time()
        if "Pause Access" in text or "Unpause Access" in text:
            if current_time - self.last_pause_action_time < self.debounce_delay:
                logging.debug("Debouncing: Ignoring rapid pause/unpause click")
                return
            self.last_pause_action_time = current_time
            self.paused = not self.paused
            new_text = "▶ Unpause Access" if self.paused else "⏸ Pause Access"
            if self.pause_btn and self.pause_btn.winfo_exists():
                try:
                    self.pause_btn.configure(text=new_text.split(" ", 1)[0] + "\n" + new_text.split(" ", 1)[1])
                    self.pause_btn.configure(command=lambda t=new_text: self.sidebar_action(t))
                    self.pause_btn.update()
                    logging.info(f"Pause state updated: {self.paused}")
                    self.root.toggle_pause()
                except Exception as e:
                    logging.error(f"Error updating pause button: {str(e)}")
            return

        self.reset_ui()

        if "Calibrate" in text:
            self.on_calibrate_callback()
        elif "Keyboard" in text:
            self.show_keyboard_area()
        elif "Phrases" in text:
            self.show_phrases_window()
        elif "Settings" in text:
            self.show_settings()
        elif "Notes" in text:
            self.show_notes()
        elif "Dashboard" in text:
            self.show_dashboard()

    def action_back(self):
        """Handle back button action."""
        logging.debug("Back button clicked")

    def action_home(self):
        """Handle home button action."""
        logging.debug("Home button clicked")

    def action_dashboard(self):
        """Handle dashboard button action."""
        logging.debug("Dashboard button clicked")

    def action_search(self):
        """Handle search button action."""
        logging.debug("Search button clicked")

    def action_light(self):
        """Handle light button action."""
        logging.debug("Light button clicked")

    def action_cloud(self):
        """Handle cloud button action."""
        logging.debug("Cloud button clicked")

    def action_paint(self):
        """Handle paint button action."""
        logging.debug("Paint button clicked")

    def action_clear(self):
        """Handle clear button action."""
        self.main_input_var.set("")
        logging.debug("Input cleared")

    def action_delete(self):
      """Handle delete button action."""
      current_pos = self.main_input.index(tk.INSERT)  # Get current cursor position
      current_text = self.main_input_var.get()
      if current_pos > 0:
        new_text = current_text[:current_pos - 1] + current_text[current_pos:]
        self.main_input_var.set(new_text)
        self.main_input.icursor(current_pos - 1)  # Move cursor back
        logging.debug(f"Character deleted, new text: '{new_text}', cursor at: {current_pos - 1}")

    def action_share(self):
        """Handle share button action."""
        logging.debug("Share button clicked")

    def get_speak_btn(self):
        """Return the speak button for external use."""
        return self.speak_btn

    def close_phrases_window(self):
        """Close the PhrasesWindow if it exists."""
        if self.phrases_window and hasattr(self.phrases_window, 'frame') and self.phrases_window.frame.winfo_exists():
            self.phrases_window.frame.grid_remove()
            logging.info("Phrases window hidden")
        self.phrases_window = None