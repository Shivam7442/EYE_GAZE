import tkinter as tk
from tkinter import ttk

class KeyboardFrame(tk.Frame):
    def __init__(self, parent, insert_key_callback, toggle_shift_callback, toggle_caps_callback, update_predictive_text_callback):
        super().__init__(parent, bg="#1E1E1E")  # Dark theme background
        self.insert_key_callback = insert_key_callback
        self.toggle_shift_callback = toggle_shift_callback
        self.toggle_caps_callback = toggle_caps_callback
        self.update_predictive_text_callback = update_predictive_text_callback
        self.caps_lock = False
        self.is_symbols = False
        self.keys = {
            'lower': {
                'row1': ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                'row2': ["a", "s", "d", "f", "g", "h", "j", "k", "l", "'"],
                'row3': ["z", "x", "c", "v", "b", "n", "m", "!", "@", "⌫"]
            },
            'upper': {
                'row1': ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                'row2': ["A", "S", "D", "F", "G", "H", "J", "K", "L", ","],
                'row3': ["Z", "X", "C", "V", "B", "N", "M", "!", "@", "⌫"]
            },
            'symbols': {
                'row1': ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                'row2': ["@", "#", "$", "%", "&", "*", "(", ")", "-", ","],
                'row3': ["!", "\"", "'", ":", ";", "/", "?", "+", "=", "⌫"]
            }
        }

        for c in range(10):
            self.grid_columnconfigure(c, weight=1, uniform="key")
        for r in range(4):
            self.grid_rowconfigure(r, weight=1)

        self.button_style = {
            'font': ("Segoe UI", 20),
            'bg': "#3A3A3A",  # Dark theme
            'fg': "white",
            'relief': "flat",
            'borderwidth': 1,
            'height': 3,
            'width': 4
        }

        self.special_button_style = {
            'font': ("Segoe UI", 16),
            'bg': "#555555",  # Dark theme
            'fg': "white",
            'relief': "raised",
            'borderwidth': 1,
            'height': 3,
            'width': 6
        }

        self.create_keyboard()
        self.button_cache = {}

    def create_keyboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        case = 'symbols' if self.is_symbols else ('upper' if self.caps_lock else 'lower')

        self.create_key_row(0, self.keys[case]['row1'], start_col=0)
        self.create_key_row(1, self.keys[case]['row2'], start_col=0)
        self.create_key_row(2, self.keys[case]['row3'], start_col=0)
        self.create_bottom_row(3)

    def create_key_row(self, row, keys, start_col=0):
        col = start_col
        for key in keys:
            if key == "⌫":
                command = lambda: (self.insert_key_callback("BACKSPACE"), self.update_predictive_text_callback())
            else:
                command = lambda k=key: (self.insert_key_callback(k), self.update_predictive_text_callback())
            b = tk.Button(self, text=key, **self.button_style, command=command)
            b.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            col += 1

    def create_bottom_row(self, row):
        buttons = [
            ("↑ Shift", self.toggle_shift_callback, 0, self.special_button_style, 2),
            ("123?#", self.toggle_symbols, 2, self.special_button_style, 1),
            ("aA Caps Lock", self.toggle_caps, 3, self.special_button_style, 1),
            ("?", lambda: (self.insert_key_callback("?"), self.update_predictive_text_callback()), 4, self.button_style, 1),
            ("Space", lambda: (self.insert_key_callback(" "), self.update_predictive_text_callback()), 5, self.special_button_style, 2),
            (".", lambda: (self.insert_key_callback("."), self.update_predictive_text_callback()), 7, self.button_style, 1),
            ("←", lambda: (self.insert_key_callback("LEFT"), self.update_predictive_text_callback()), 8, self.special_button_style, 1),
            ("→", lambda: (self.insert_key_callback("RIGHT"), self.update_predictive_text_callback()), 9, self.special_button_style, 1),
        ]

        for text, cmd, col, style, colspan in buttons:
            btn = tk.Button(self, text=text, command=cmd, **style)
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)

    def toggle_caps(self):
        self.caps_lock = not self.caps_lock
        self.toggle_caps_callback()
        self.create_keyboard()

    def toggle_symbols(self):
        self.is_symbols = not self.is_symbols
        self.create_keyboard()