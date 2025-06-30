import tkinter as tk
from ui_manager import UIManager
from cursor_manager import CursorManager
from dwell_timer import DwellTimer
from calibration_demo import CalibrationDemo
import cv2
import numpy as np
import logging
import os

class EyeTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye Tracking AAC Application")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#121212")

        # Initialize logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Starting EyeTrackingApp")

        # Initialize components
        self.cursor_manager = CursorManager(self.root)
        self.dwell_timer = DwellTimer(self.root, self.handle_dwell)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Initialize UI
        self.ui_manager = UIManager(
            self.root,
            on_calibrate_callback=self.run_calibration,
            show_debug_callback=self.show_debug
        )

        # Video capture
        self.cap = None
        self.is_running = False
        self.is_paused = False
        self.calibration_demo = None
        self.calibration_canvas = None

    def run_calibration(self):
        """Run calibration in Tkinter canvas."""
        logging.info("Starting calibration")
        self.is_running = False
        
        # Hide cursor during calibration
        self.cursor_manager.hide_cursor()
        
        # Hide sidebar and main frame contents
        if hasattr(self.ui_manager, 'sidebar'):
            self.ui_manager.sidebar.grid_remove()
        if hasattr(self.ui_manager, 'main_frame'):
            for widget in self.ui_manager.main_frame.winfo_children():
                widget.grid_remove()

        # Initialize camera
        if self.cap is None or not self.cap.isOpened():
            logging.debug("Opening webcam")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logging.error("Failed to open webcam")
                self.ui_manager.show_message("Error", "Unable to open webcam")
                return

        # Create calibration canvas in main frame
        self.calibration_canvas = tk.Canvas(self.ui_manager.main_frame, bg="black", highlightthickness=0)
        self.calibration_canvas.grid(row=0, column=0, sticky="nsew", rowspan=3)
        self.ui_manager.main_frame.grid_rowconfigure(0, weight=1)
        self.ui_manager.main_frame.grid_columnconfigure(0, weight=1)

        # Initialize calibration
        self.calibration_demo = CalibrationDemo(
            self.root, self.calibration_canvas, self.close, self.screen_width,
            self.screen_height, self.calibration_complete
        )
        self.calibration_demo.start_calibration()

        # Start frame processing
        self.is_running = True
        self.update_gaze()

    def calibration_complete(self):
        """Handle calibration completion."""
        logging.info("Calibration completed, resuming UI")
        if self.calibration_canvas:
            self.calibration_canvas.destroy()
            self.calibration_canvas = None
        # Restore sidebar
        if hasattr(self.ui_manager, 'sidebar'):
            self.ui_manager.sidebar.grid()
        # Show cursor again
        self.cursor_manager.show_cursor()
        # Reset cursor position to center of screen
        self.cursor_manager.move_cursor(self.screen_width // 2, self.screen_height // 2)
        self.ui_manager.show_keyboard_area()

    def update_gaze(self):
        """Update gaze or process calibration."""
        if not self.is_running or self.is_paused:
            self.root.after(10, self.update_gaze)
            return

        if not self.cap or not self.cap.isOpened():
            logging.debug("No active camera")
            self.root.after(10, self.update_gaze)
            return

        ret, frame = self.cap.read()
        if not ret:
            logging.error("Failed to capture frame")
            self.root.after(10, self.update_gaze)
            return

        # Mirror and resize frame
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (self.screen_width, self.screen_height))

        # Process frame
        eye_features = None
        try:
            if self.calibration_demo and self.calibration_canvas:
                eye_features = self.calibration_demo.process_frame(frame)
            elif self.calibration_demo:
                eye_features = self.calibration_demo.face_detector.get_eye_features(frame)
        except Exception as e:
            logging.error(f"Error processing frame: {e}")

        if eye_features is not None and not (self.calibration_demo and self.calibration_demo.testing_accuracy):
            try:
                prediction = self.calibration_demo.ridge_regression.predict(eye_features)
                if prediction:
                    filtered_pred = self.calibration_demo.kalman_filter.update([prediction['x'], prediction['y']])
                    x = max(0, min(int(filtered_pred[0]), self.screen_width - 1))
                    y = max(0, min(int(filtered_pred[1]), self.screen_height - 1))
                    self.cursor_manager.move_cursor(x, y)
                    self.dwell_timer.update_position(x, y)
            except Exception as e:
                logging.error(f"Error in gaze prediction: {e}")

        self.root.after(10, self.update_gaze)

    def handle_dwell(self, x, y):
        """Handle dwell events."""
        logging.debug(f"Dwell at ({x}, {y})")
        self.cursor_manager.simulate_click(x, y)

    def show_debug(self):
        """Show debug info."""
        logging.info("Debug requested")
        # Implement debug logic

    def toggle_pause(self):
        """Toggle pause."""
        self.is_paused = not self.is_paused
        logging.info(f"Pause state: {self.is_paused}")

    def close(self):
        """Clean up."""
        logging.info("Closing app")
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        if self.calibration_canvas:
            self.calibration_canvas.destroy()
        self.root.destroy()

if __name__ == "__main__":
    if not os.path.exists("src"):
        os.makedirs("src")
    root = tk.Tk()
    app = EyeTrackingApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()