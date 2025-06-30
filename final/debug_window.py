import tkinter as tk
from tkinter import ttk
import logging
import sys
import psutil
from datetime import datetime

# Set up detailed logging (same as in main.py to ensure consistency)
log_filename = f'eye_tracking_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

class DebugWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Debug Information")
        self.geometry("800x600")
        self.configure(bg="#1E1E1E")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.status_tab = tk.Frame(self.notebook, bg="#2D2D2D")
        self.notebook.add(self.status_tab, text="Status")

        self.log_tab = tk.Frame(self.notebook, bg="#2D2D2D")
        self.notebook.add(self.log_tab, text="Log")

        self.status_text = tk.Text(
            self.status_tab,
            bg="#2D2D2D",
            fg="#FFFFFF",
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_text = tk.Text(
            self.log_tab,
            bg="#2D2D2D",
            fg="#FFFFFF",
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        for widget in [self.status_text, self.log_text]:
            scrollbar = ttk.Scrollbar(widget, command=widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            widget.configure(yscrollcommand=scrollbar.set)

        self.button_frame = tk.Frame(self, bg="#1E1E1E")
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(
            self.button_frame,
            text="Clear Log",
            command=self.clear_log,
            bg="#3D3D3D",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            self.button_frame,
            text="Close",
            command=self.destroy,
            bg="#3D3D3D",
            fg="white",
            relief=tk.FLAT
        ).pack(side=tk.RIGHT, padx=5)

        self.attributes('-topmost', True)
        self.update_debug_info()
        self.update_log()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def update_debug_info(self):
        try:
            self.status_text.delete(1.0, tk.END)
            app = self.master

            window_info = f"Window State:\n"
            window_info += f"Size: {app.winfo_width()}x{app.winfo_height()}\n"
            window_info += f"Screen Size: {app.winfo_screenwidth()}x{app.winfo_screenheight()}\n"
            window_info += f"Window State: {app.state()}\n"
            window_info += f"Window Manager: {app.winfo_manager()}\n"

            cursor_canvas = app.cursor_manager.get_cursor_canvas()
            canvas_info = f"\nCursor Canvas State:\n"
            if cursor_canvas:
                canvas_info += f"Canvas exists: Yes\n"
                canvas_info += f"Canvas size: {cursor_canvas.winfo_width()}x{cursor_canvas.winfo_height()}\n"
                canvas_info += f"Canvas ready: {app.cursor_manager.is_cursor_canvas_ready()}\n"
                canvas_info += f"Cursor visible: {app.gaze_tracker.cursor_visible}\n"
                canvas_info += f"Canvas manager: {cursor_canvas.winfo_manager()}\n"
                canvas_info += f"Canvas parent: {cursor_canvas.winfo_parent()}\n"
                canvas_info += f"Canvas children: {len(cursor_canvas.winfo_children())}\n"
            else:
                canvas_info += f"Canvas exists: No\n"

            frame_info = f"\nCursor Frame State:\n"
            frame_info += f"Frame exists: Not applicable (using Toplevel window)\n"

            cal_info = f"\nCalibration State:\n"
            cal_info += f"Calibration running: {app.calibrator.calibration_running}\n"
            cal_info += f"Gaze tracking: {app.gaze_tracker.gaze_tracking}\n"
            cal_info += f"Camera available: {app.calibrator.cap is not None and app.calibrator.cap.isOpened()}\n"

            thread_info = f"\nThread State:\n"
            thread_info += f"Calibration thread: {'Running' if app.calibrator.calibration_thread and app.calibrator.calibration_thread.is_alive() else 'Not running'}\n"
            thread_info += f"Gaze thread: {'Running' if app.gaze_tracker.gaze_thread and app.gaze_tracker.gaze_thread.is_alive() else 'Not running'}\n"

            process = psutil.Process()
            mem_info = f"\nMemory Usage:\n"
            mem_info += f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB\n"
            mem_info += f"CPU: {process.cpu_percent()}%\n"

            debug_text = f"{window_info}\n{canvas_info}\n{frame_info}\n{cal_info}\n{thread_info}\n{mem_info}"
            self.status_text.insert(tk.END, debug_text)

        except Exception as e:
            self.status_text.insert(tk.END, f"Error updating debug info: {str(e)}\n")

        self.after(1000, self.update_debug_info)

    def update_log(self):
        try:
            with open(log_filename, 'r') as f:
                lines = f.readlines()
                last_lines = lines[-50:] if len(lines) > 50 else lines
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, ''.join(last_lines))
        except Exception as e:
            self.log_text.insert(tk.END, f"Error reading log: {str(e)}\n")

        self.after(1000, self.update_log)