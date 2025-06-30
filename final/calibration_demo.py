import tkinter as tk
import cv2
import numpy as np
import logging
from src.face_mesh import FaceMeshDetector
from src.ridge_regression import RidgeRegression
from src.kalman_filter import KalmanFilter

class CalibrationDemo:
    def __init__(self, root, canvas, close_callback, screen_width, screen_height, calibration_complete_callback):
        self.root = root
        self.canvas = canvas
        self.close_callback = close_callback
        self.calibration_complete_callback = calibration_complete_callback
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.face_detector = FaceMeshDetector()
        self.ridge_regression = RidgeRegression()
        self.kalman_filter = KalmanFilter()
        
        # Calibration state
        self.calibration_points = []
        self.current_point = 0
        self.clicks_per_point = 5
        self.clicks = 0
        self.calibrating = False
        self.testing_accuracy = False
        self.accuracy_predictions = []
        self.accuracy_start_time = 0
        self.test_duration = 5
        self.showing_results = False
        self.accuracy_result = 0.0
        self.showing_calibration_complete = False
        self.current_frame = None
        
        # Setup points
        self.setup_calibration_points()
        
        # Bind click
        self.canvas.bind("<Button-1>", self.handle_click)
        
    def setup_calibration_points(self):
        """Set up 9 points."""
        margin = int(min(self.screen_width, self.screen_height) * 0.15)
        x_positions = np.linspace(margin, self.screen_width - margin, 3)
        y_positions = np.linspace(margin, self.screen_height - margin, 3)
        self.calibration_points = [(int(x), int(y)) for y in y_positions for x in x_positions]

    def draw_calibration_point(self):
        """Draw current point."""
        if self.current_point < len(self.calibration_points):
            x, y = self.calibration_points[self.current_point]
            # Clear canvas and set black background
            self.canvas.delete("all")
            self.canvas.configure(bg="black")
            
            # Draw calibration point
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="red", outline="white", width=2)
            self.canvas.create_text(x, y-20, text=f"Clicks: {self.clicks}/{self.clicks_per_point}", 
                                  fill="white", font=("Segoe UI", 12))
        self.draw_close_button()

    def draw_close_button(self):
        """Draw close cross."""
        self.canvas.create_line(10, 10, 30, 30, fill="red", width=3)
        self.canvas.create_line(10, 30, 30, 10, fill="red", width=3)

    def calculate_accuracy(self, predictions, target_point):
        """Calculate accuracy."""
        if not predictions:
            return 0.0
        distances = [np.sqrt((pred['x'] - target_point[0])**2 + (pred['y'] - target_point[1])**2) for pred in predictions]
        avg_distance = np.mean(distances)
        max_distance = np.sqrt(self.screen_width**2 + self.screen_height**2)
        accuracy = max(0, 100 * (1 - avg_distance / max_distance))
        return round(accuracy, 1)

    def start_accuracy_test(self):
        """Start accuracy test."""
        self.testing_accuracy = True
        self.accuracy_predictions = []
        self.accuracy_start_time = cv2.getTickCount() / cv2.getTickFrequency()
        self.test_target = (self.screen_width // 2, self.screen_height // 2)
        logging.info("Starting accuracy test")
        self.draw_accuracy_test()

    def draw_accuracy_test(self):
        """Draw accuracy test."""
        # Clear canvas and set black background
        self.canvas.delete("all")
        self.canvas.configure(bg="black")

        elapsed = cv2.getTickCount() / cv2.getTickFrequency() - self.accuracy_start_time
        pulse = abs(np.sin(elapsed * 2)) * 5 + 15
        self.canvas.create_oval(self.test_target[0]-pulse, self.test_target[1]-pulse,
                               self.test_target[0]+pulse, self.test_target[1]+pulse,
                               fill="red", outline="white", width=2)
        self.canvas.create_text(self.screen_width//2, self.screen_height//2-100,
                               text="Stare at red dot", fill="white", font=("Segoe UI", 16))
        remaining = max(0, self.test_duration - elapsed)
        self.canvas.create_text(self.screen_width//2, self.screen_height//2+100,
                               text=f"{int(remaining) + 1}", fill="white", font=("Segoe UI", 36))
        for pred in self.accuracy_predictions:
            self.canvas.create_oval(pred['x']-3, pred['y']-3, pred['x']+3, pred['y']+3, 
                                  fill="green", outline="white", width=1)
        self.draw_close_button()
        if elapsed < self.test_duration:
            self.root.after(100, self.draw_accuracy_test)
        else:
            self.accuracy_result = self.calculate_accuracy(self.accuracy_predictions, self.test_target)
            self.testing_accuracy = False
            self.showing_results = True
            self.draw_results()

    def draw_results(self):
        """Draw results."""
        # Clear canvas and set black background
        self.canvas.delete("all")
        self.canvas.configure(bg="black")

        self.canvas.create_text(self.screen_width//2, self.screen_height//2-50,
                               text=f"Accuracy: {self.accuracy_result}%", 
                               fill="white", font=("Segoe UI", 24))
        button_width, button_height = 200, 80
        button_spacing = 50
        total_width = button_width * 2 + button_spacing
        start_x = self.screen_width//2 - total_width//2
        self.recalibrate_button = self.canvas.create_rectangle(
            start_x, self.screen_height//2+50, start_x+button_width, self.screen_height//2+50+button_height,
            fill="green", outline="white", width=2)
        self.canvas.create_text(start_x+button_width//2, self.screen_height//2+50+button_height//2,
                               text="Recalibrate", fill="black", font=("Segoe UI", 14))
        self.continue_button = self.canvas.create_rectangle(
            start_x+button_width+button_spacing, self.screen_height//2+50,
            start_x+2*button_width+button_spacing, self.screen_height//2+50+button_height,
            fill="orange", outline="white", width=2)
        self.canvas.create_text(start_x+1.5*button_width+button_spacing, self.screen_height//2+50+button_height//2,
                               text="Continue", fill="black", font=("Segoe UI", 14))
        self.canvas.create_text(self.screen_width//2, self.screen_height//2+200,
                               text="Click Recalibrate or Continue", 
                               fill="white", font=("Segoe UI", 14))
        self.draw_close_button()

    def draw_calibration_complete(self):
        """Draw complete screen."""
        # Clear canvas and set black background
        self.canvas.delete("all")
        self.canvas.configure(bg="black")

        self.canvas.create_text(self.screen_width//2, self.screen_height//2-100,
                               text="Calibration Complete!", 
                               fill="white", font=("Segoe UI", 24))
        button_width, button_height = 300, 80
        button_x = self.screen_width//2 - button_width//2
        button_y = self.screen_height//2 + 50
        self.accuracy_button = self.canvas.create_rectangle(
            button_x, button_y, button_x+button_width, button_y+button_height, 
            fill="orange", outline="white", width=2)
        self.canvas.create_text(button_x+button_width//2, button_y+button_height//2,
                               text="Calculate Accuracy", fill="black", font=("Segoe UI", 14))
        self.canvas.create_text(self.screen_width//2, self.screen_height//2+200,
                               text="Click Calculate Accuracy", 
                               fill="white", font=("Segoe UI", 14))
        self.draw_close_button()

    def start_calibration(self):
        """Start calibration."""
        self.calibrating = True
        self.current_point = 0
        self.clicks = 0
        self.ridge_regression.clear_data()
        self.kalman_filter.reset()
        self.draw_calibration_point()
        logging.info("Calibration started")

    def finish_calibration(self):
        """Finish calibration."""
        self.calibrating = False
        self.ridge_regression.train()
        self.showing_calibration_complete = True
        self.draw_calibration_complete()
        logging.info("Calibration completed")

    def process_frame(self, frame):
        """Process frame."""
        if not self.calibrating and not self.testing_accuracy:
            return None
        self.current_frame = frame
        try:
            eye_features = self.face_detector.get_eye_features(frame)
            if eye_features is not None and self.testing_accuracy:
                prediction = self.ridge_regression.predict(eye_features)
                if prediction:
                    self.accuracy_predictions.append(prediction)
            return eye_features
        except Exception as e:
            logging.error(f"Error processing frame: {e}")
            return None

    def handle_click(self, event):
        """Handle clicks."""
        x, y = event.x, event.y
        logging.debug(f"Click at ({x}, {y}), calibrating: {self.calibrating}")
        if 10 <= x <= 30 and 10 <= y <= 30:
            self.close_callback()
            return
        if self.showing_calibration_complete:
            button_width, button_height = 300, 80
            button_x = self.screen_width//2 - button_width//2
            button_y = self.screen_height//2 + 50
            if button_x <= x <= button_x+button_width and button_y <= y <= button_y+button_height:
                self.showing_calibration_complete = False
                self.start_accuracy_test()
                return
        elif self.showing_results:
            button_width, button_height = 200, 80
            button_spacing = 50
            total_width = button_width * 2 + button_spacing
            start_x = self.screen_width//2 - total_width//2
            if (start_x <= x <= start_x+button_width and
                self.screen_height//2+50 <= y <= self.screen_height//2+50+button_height):
                self.showing_results = False
                self.start_calibration()
                return
            if (start_x+button_width+button_spacing <= x <= start_x+2*button_width+button_spacing and
                self.screen_height//2+50 <= y <= self.screen_height//2+50+button_height):
                self.showing_results = False
                self.canvas.delete("all")
                self.calibration_complete_callback()
                return
        if not self.calibrating or self.current_frame is None:
            logging.debug("Click ignored: not calibrating or no frame")
            return
        if self.current_point < len(self.calibration_points):
            target_x, target_y = self.calibration_points[self.current_point]
            if abs(x - target_x) < 20 and abs(y - target_y) < 20:
                try:
                    eye_features = self.face_detector.get_eye_features(self.current_frame)
                    if eye_features is not None:
                        self.ridge_regression.add_data_point(eye_features, (target_x, target_y), 'click')
                        self.clicks += 1
                        if self.clicks >= self.clicks_per_point:
                            self.current_point += 1
                            self.clicks = 0
                            if self.current_point >= len(self.calibration_points):
                                self.finish_calibration()
                            else:
                                self.draw_calibration_point()
                        else:
                            self.draw_calibration_point()
                except Exception as e:
                    logging.error(f"Error processing click: {e}")