import tkinter as tk
from tkinter import ttk, messagebox
import pyttsx3
import logging

class VoiceSettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Voice Settings")
        self.window.configure(bg="#121212")
        
        # Set window size and position
        window_width = 400
        window_height = 300
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.current_voice = 0
        
        # Log available voices
        logging.info("Available voices:")
        for i, voice in enumerate(self.voices):
            logging.info(f"{i}: {voice.name} ({voice.id})")
        
        # Check for Indian and British English voices
        self.has_indian_english = any('en-IN' in voice.id or 'India' in voice.name for voice in self.voices)
        self.has_british_english = any('en-GB' in voice.id or 'UK' in voice.name or 'British' in voice.name for voice in self.voices)
        
        if not (self.has_indian_english and self.has_british_english):
            missing = []
            if not self.has_indian_english:
                missing.append("Indian English")
            if not self.has_british_english:
                missing.append("British English")
            messagebox.showwarning(
                "Missing Voices",
                f"The following voices are not installed: {', '.join(missing)}. "
                "Please install additional TTS voices or use an external TTS service."
            )
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.window,
            text="Voice Settings",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#121212"
        )
        title_label.pack(pady=20)
        
        # Voice selection frame
        voice_frame = tk.Frame(self.window, bg="#121212")
        voice_frame.pack(pady=20, padx=20, fill="x")
        
        # Voice selection label
        voice_label = tk.Label(
            voice_frame,
            text="Select Voice:",
            font=("Segoe UI", 12),
            fg="white",
            bg="#121212"
        )
        voice_label.pack(anchor="w", pady=(0, 10))
        
        # Voice selection dropdown
        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(
            voice_frame,
            textvariable=self.voice_var,
            state="readonly",
            width=30,
            font=("Segoe UI", 10)
        )
        
        # Get voice names and improve accent detection
        voice_names = []
        self.voice_accent_map = {}  # Store voice index to accent mapping
        for i, voice in enumerate(self.voices):
            voice_name = voice.name
            accent = "Unknown"
            # Improved accent detection
            if 'en-US' in voice.id or 'US' in voice.name or 'American' in voice.name:
                accent = "US English"
            elif 'en-GB' in voice.id or 'UK' in voice.name or 'British' in voice.name:
                accent = "British English"
            elif 'en-IN' in voice.id or 'India' in voice.name or 'Indian' in voice.name:
                accent = "Indian English"
            voice_names.append(f"{voice_name} ({accent})")
            self.voice_accent_map[i] = accent
        
        self.voice_dropdown['values'] = voice_names
        # Set default to British or Indian English if available
        for i, accent in self.voice_accent_map.items():
            if accent in ["British English", "Indian English"]:
                self.current_voice = i
                break
        self.voice_dropdown.current(self.current_voice)
        self.voice_dropdown.pack(fill="x", pady=5)
        
        # Test button
        test_button = tk.Button(
            voice_frame,
            text="Test Voice",
            font=("Segoe UI", 10),
            fg="white",
            bg="#4CAF50",
            activebackground="#45A049",
            activeforeground="white",
            relief="flat",
            command=self.test_voice
        )
        test_button.pack(pady=10)
        
        # Save button
        save_button = tk.Button(
            voice_frame,
            text="Save Voice",
            font=("Segoe UI", 10),
            fg="white",
            bg="#2196F3",
            activebackground="#1E88E5",
            activeforeground="white",
            relief="flat",
            command=self.save_voice
        )
        save_button.pack(pady=5)
        
        # Close button
        close_button = tk.Button(
            self.window,
            text="Close",
            font=("Segoe UI", 10),
            fg="white",
            bg="#3A3A3A",
            activebackground="#555555",
            activeforeground="white",
            relief="flat",
            command=self.window.destroy
        )
        close_button.pack(pady=20)
        
    def test_voice(self):
        """Test the selected voice."""
        try:
            selected_index = self.voice_dropdown.current()
            if selected_index >= 0:
                self.engine.setProperty('voice', self.voices[selected_index].id)
                self.engine.say("This is a test of the selected voice.")
                self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Error testing voice: {str(e)}")
            messagebox.showerror("Error", f"Failed to test voice: {str(e)}")
            
    def save_voice(self):
        """Save the selected voice for persistent use."""
        try:
            selected_index = self.voice_dropdown.current()
            if selected_index >= 0:
                self.current_voice = selected_index
                # Optionally save to a config file or database
                logging.info(f"Saved voice: {self.voices[selected_index].name} ({self.voice_accent_map[selected_index]})")
                messagebox.showinfo("Success", "Voice saved successfully!")
        except Exception as e:
            logging.error(f"Error saving voice: {str(e)}")
            messagebox.showerror("Error", f"Failed to save voice: {str(e)}")
            
    def get_selected_voice(self):
        """Return the currently selected voice index."""
        return self.voice_dropdown.current()