import tkinter as tk
from tkinter import ttk
import pyttsx3
import logging
from keyboard import KeyboardFrame

class PhrasesWindow:
    def __init__(self, parent, main_text_widget):
        logging.info("Initializing PhrasesWindow")
        # Create a Frame to embed in the parent
        self.frame = tk.Frame(parent, bg="#1E1E1E")
        self.frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)  # Ensure frame is gridded
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        
        # Store references
        self.main_text_widget = main_text_widget
        self.ui_manager = parent.ui_manager if hasattr(parent, 'ui_manager') else None
        logging.debug(f"UI manager available: {self.ui_manager is not None}")
        
        # Initialize text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            logging.info("Text-to-speech engine initialized")
        except Exception as e:
            logging.error(f"Error initializing text-to-speech: {str(e)}")
        
        # Navigation bar
        self.nav_frame = tk.Frame(self.frame, bg="#2A2A2A")
        self.nav_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        tk.Button(self.nav_frame, text="← Backward", font=("Segoe UI", 12), bg="#3A3A3A", fg="white", 
                  activebackground="#555555", command=self.backward_slide).grid(row=0, column=0, sticky="ew", padx=5)
        tk.Button(self.nav_frame, text="Forward →", font=("Segoe UI", 12), bg="#3A3A3A", fg="white", 
                  activebackground="#555555", command=self.forward_slide).grid(row=0, column=1, sticky="ew", padx=5)
        
        # Create main frame for the grid
        self.main_frame = ttk.Frame(self.frame, style="TFrame")
        self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Define button colors
        self.button_colors = {
            "Questions": "#4682B4",
            "People": "#BDB76B",
            "Actions": "#6B8E23",
            "Descriptions": "#CD853F",
            "Word Forms": "#CD5C5C",
        }
        
        # Define button data
        self.pages = [
            [
                [("what", "❓"), ("I", "👤"), ("is", "—"), ("want", "🙌"), ("not", "🚫")],
                [("who", "👤❓"), ("you", "👈"), ("can", "💪"), ("like", "😊"), ("more", "➕")],
                [("where", "📍❓"), ("it", "⬜"), ("do", "🏃"), ("go", "➡️"), ("a", "a")],
                [("when", "⏰❓"), ("he", "👨"), ("have", "🤲"), ("stop", "✋"), ("and", "&")],
                [("why", "❔"), ("she", "👩"), ("help", "🤝"), ("put", "⤴️"), ("the", "the")]
            ],
            [
                [("how", "❓"), ("we", "👥"), ("are", "—"), ("need", "🆘"), ("yes", "✔️")],
                [("which", "🤔"), ("they", "👥"), ("will", "⏳"), ("know", "🧠"), ("some", "🔢")],
                [("there", "📍"), ("this", "👇"), ("make", "🛠️"), ("come", "⬅️"), ("an", "an")],
                [("now", "⏰"), ("him", "👨"), ("get", "📥"), ("look", "👀"), ("or", "or")],
                [("because", "➡️"), ("her", "👩"), ("give", "🎁"), ("say", "💬"), ("in", "in")]
            ]
        ]
        
        self.current_page = 0
        self.buttons = self.pages[self.current_page]
        
        # State for edit
        self.editing_row = None
        self.editing_col = None
        self.temp_input = tk.StringVar()
        
        # Create the layout
        try:
            self.create_communication_board()
            logging.info("Communication board created")
        except Exception as e:
            logging.error(f"Error creating communication board: {str(e)}")
        
        # Keyboard (initially hidden)
        try:
            self.keyboard = KeyboardFrame(
                self.frame,
                insert_key_callback=self.insert_key,
                toggle_shift_callback=lambda: None,
                toggle_caps_callback=lambda: None,
                update_predictive_text_callback=lambda: None
            )
            logging.info("Keyboard initialized")
        except Exception as e:
            logging.error(f"Error initializing keyboard: {str(e)}")
    
    def create_communication_board(self):
        logging.debug("Creating communication board")
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        for row in range(5):
            self.main_frame.grid_rowconfigure(row, weight=1)
            for col in range(5):
                self.main_frame.grid_columnconfigure(col, weight=1)
                text, symbol = self.buttons[row][col]
                
                if col == 0:
                    color = self.button_colors["Questions"]
                elif col == 1:
                    color = self.button_colors["People"]
                elif col == 2:
                    color = self.button_colors["Actions"]
                elif col == 3:
                    color = self.button_colors["Descriptions"]
                else:
                    color = self.button_colors["Word Forms"]
                
                btn_frame = tk.Frame(self.main_frame, bg=color, relief="raised", borderwidth=2)
                btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                btn = tk.Button(
                    btn_frame,
                    text=f"{symbol}\n\n{text}",
                    font=("Segoe UI", 14, "bold"),
                    bg=color,
                    fg="white",
                    relief="flat",
                    wraplength=100,
                    justify="center",
                    command=lambda t=text: self.button_action(t)
                )
                btn.pack(fill="both", expand=True, padx=5, pady=5)
                
                btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg="#555555"))
                btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
                
                edit_btn = tk.Button(
                    btn_frame, text="Edit", font=("Segoe UI", 10), bg="#3A3A3A", fg="white",
                    activebackground="#555555", command=lambda r=row, c=col: self.show_edit_block(r, c)
                )
                edit_btn.pack(side="bottom", padx=2, pady=2)
    
    def forward_slide(self):
        logging.debug("Navigating to next page")
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
        else:
            self.pages.append([[("", "") for _ in range(5)] for _ in range(5)])
            self.current_page += 1
        self.buttons = self.pages[self.current_page]
        self.create_communication_board()
    
    def backward_slide(self):
        logging.debug("Navigating to previous page")
        if self.current_page > 0:
            self.current_page -= 1
            self.buttons = self.pages[self.current_page]
            self.create_communication_board()
    
    def show_edit_block(self, row, col):
        logging.debug(f"Showing edit block for row {row}, col {col}")
        self.editing_row = row
        self.editing_col = col
        self.temp_input.set(self.buttons[row][col][0])
        self.nav_frame.grid_remove()
        self.main_frame.grid_remove()

        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=1)

        input_frame = tk.Frame(self.frame, bg="#1E1E1E")
        input_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)
        input_frame.grid_columnconfigure(2, weight=0)

        tk.Entry(
            input_frame,
            textvariable=self.temp_input,
            font=("Segoe UI", 18),
            bg="#3A3A3A",
            fg="white",
            relief="flat"
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        tk.Button(
            input_frame,
            text="Save",
            font=("Segoe UI", 12),
            bg="#4CAF50",
            fg="white",
            activebackground="#45A049",
            command=self.save_edit_block
        ).grid(row=0, column=1, padx=(0, 5), pady=5)

        tk.Button(
            input_frame,
            text="Cancel",
            font=("Segoe UI", 12),
            bg="#F44336",
            fg="white",
            activebackground="#D32F2F",
            command=self.return_to_blocks
        ).grid(row=0, column=2, padx=(0, 5), pady=5)

        self.keyboard.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    
    def save_edit_block(self):
        logging.debug("Saving edited block")
        edited_text = self.temp_input.get().strip()
        if edited_text:
            symbol = self.buttons[self.editing_row][self.editing_col][1]
            self.pages[self.current_page][self.editing_row][self.editing_col] = (edited_text, symbol)
        self.temp_input.set("")
        self.editing_row = None
        self.editing_col = None
        self.return_to_blocks()
    
    def return_to_blocks(self):
        logging.debug("Returning to communication board")
        self.keyboard.grid_remove()
        for widget in self.frame.winfo_children():
            if widget not in [self.nav_frame, self.main_frame, self.keyboard]:
                widget.destroy()
        self.nav_frame.grid()
        self.main_frame.grid()
        self.frame.grid_rowconfigure(1, weight=1)
        self.create_communication_board()
    
    def insert_key(self, key):
        logging.debug(f"Inserting key: {key}")
        if key == "LEFT" or key == "RIGHT":
            pass
        elif key == "BACKSPACE":
            current = self.temp_input.get()
            self.temp_input.set(current[:-1])
        else:
            current = self.temp_input.get()
            self.temp_input.set(current + key.upper() if self.keyboard.caps_lock else current + key)
    
    def button_action(self, phrase):
        logging.debug(f"Button action for phrase: {phrase}")
        self.speak_phrase(phrase)
        self.add_to_text(phrase)
    
    def add_to_text(self, phrase):
        try:
            if self.ui_manager and hasattr(self.ui_manager, 'main_input_var'):
                current_text = self.ui_manager.main_input_var.get().strip()
                new_text = current_text + " " + phrase if current_text else phrase
                self.ui_manager.main_input_var.set(new_text)
                if hasattr(self.ui_manager, 'update_suggestions'):
                    self.ui_manager.update_suggestions()
                logging.info(f"Added phrase to main input: {phrase}")
            else:
                logging.error("UI manager or main input not found")
        except Exception as e:
            logging.error(f"Error adding phrase to text: {str(e)}")
    
    def speak_phrase(self, phrase):
        try:
            if self.ui_manager and hasattr(self.ui_manager, 'current_voice_index'):
                self.engine.setProperty('voice', self.ui_manager.voices[self.ui_manager.current_voice_index].id)
            self.engine.say(phrase)
            self.engine.runAndWait()
            logging.info(f"Spoke phrase: {phrase}")
        except Exception as e:
            logging.error(f"Error in text-to-speech: {str(e)}")
    
    def close(self):
        logging.info("Closing PhrasesWindow")
        try:
            self.engine.stop()
        except:
            pass
        self.frame.destroy()