import cv2
import numpy as np
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.face_mesh import FaceMeshDetector
from src.ridge_regression import RidgeRegression
from src.kalman_filter import KalmanFilter

class CalibrationDemo:
    def __init__(self):
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
        self.test_duration = 5  # seconds to test accuracy
        self.showing_results = False
        self.accuracy_result = 0.0
        self.showing_calibration_complete = False  # New state for showing calibration complete screen
        
        # Window setup
        self.window_name = "Eye Tracking Calibration"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Initialize with default dimensions, will be updated in run()
        self.screen_width = 1920  # Default width
        self.screen_height = 1080  # Default height
        
        # Set up calibration points (9-point grid)
        self.setup_calibration_points()
        
    def setup_calibration_points(self):
        """Set up the 9 calibration points in a grid."""
        # Calculate grid positions using screen dimensions
        margin = int(min(self.screen_width, self.screen_height) * 0.15)  # 15% margin for better visibility
        x_positions = np.linspace(margin, self.screen_width - margin, 3)
        y_positions = np.linspace(margin, self.screen_height - margin, 3)
        
        # Create grid points
        self.calibration_points = []
        for y in y_positions:
            for x in x_positions:
                # Ensure points are within screen bounds
                x = max(0, min(int(x), self.screen_width - 1))
                y = max(0, min(int(y), self.screen_height - 1))
                self.calibration_points.append((x, y))
    
    def update_window_dimensions(self):
        """Update window dimensions after window is displayed."""
        try:
            # Get the actual window dimensions
            _, _, width, height = cv2.getWindowImageRect(self.window_name)
            if width > 0 and height > 0:  # Only update if we got valid dimensions
                self.screen_width = width
                self.screen_height = height
                # Recalculate calibration points with new dimensions
                self.setup_calibration_points()
        except:
            pass  # Keep existing dimensions if we can't get window size
    
    def draw_calibration_point(self, frame):
        """Draw the current calibration point."""
        if self.current_point < len(self.calibration_points):
            x, y = self.calibration_points[self.current_point]
            # Draw point
            cv2.circle(frame, (x, y), 10, (0, 0, 255), -1)
            # Draw click counter
            cv2.putText(frame, f"Clicks: {self.clicks}/{self.clicks_per_point}",
                       (x - 30, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    def calculate_accuracy(self, predictions, target_point):
        """Calculate accuracy based on predictions during center point test."""
        if not predictions:
            return 0.0
            
        # Calculate average distance from target point
        distances = []
        for pred in predictions:
            dx = pred['x'] - target_point[0]
            dy = pred['y'] - target_point[1]
            distance = np.sqrt(dx*dx + dy*dy)
            distances.append(distance)
            
        avg_distance = np.mean(distances)
        max_distance = np.sqrt(self.screen_width**2 + self.screen_height**2)
        
        # Convert to accuracy percentage (100% = perfect accuracy, 0% = maximum error)
        accuracy = max(0, 100 * (1 - avg_distance / max_distance))
        return round(accuracy, 1)

    def start_accuracy_test(self):
        """Start the accuracy test with center point."""
        self.testing_accuracy = True
        self.accuracy_predictions = []
        self.accuracy_start_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        # Calculate center point
        self.test_target = (self.screen_width // 2, self.screen_height // 2)
        
        # Show instructions
        print("\nStare at the center point for 5 seconds...")
        print("Testing accuracy...")

    def draw_accuracy_test(self, frame):
        """Draw the center point and accuracy test UI."""
        # Create a semi-transparent overlay
        overlay = frame.copy()
        
        # Draw center point with pulsing effect
        elapsed = cv2.getTickCount() / cv2.getTickFrequency() - self.accuracy_start_time
        pulse = abs(np.sin(elapsed * 2)) * 5 + 15  # Pulsing radius between 15-20
        cv2.circle(overlay, self.test_target, int(pulse), (0, 0, 255), -1)
        
        # Draw guidance message
        msg = "Stare at the red dot in the center"
        cv2.putText(overlay, msg, 
                   (self.screen_width//2 - 200, self.screen_height//2 - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw large timer
        remaining = max(0, self.test_duration - elapsed)
        timer_text = f"{int(remaining) + 1}"
        cv2.putText(overlay, timer_text,
                   (self.screen_width//2 - 50, self.screen_height//2 + 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 4)
        
        # Draw current predictions
        for pred in self.accuracy_predictions:
            cv2.circle(overlay, (int(pred['x']), int(pred['y'])), 3, (0, 255, 0), -1)
        
        # Apply overlay with transparency
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    def draw_results(self, frame):
        """Draw the accuracy results and recalibration/continue buttons."""
        # Create a semi-transparent overlay
        overlay = frame.copy()
        
        # Draw accuracy result
        result_text = f"Accuracy: {self.accuracy_result}%"
        cv2.putText(overlay, result_text,
                   (self.screen_width//2 - 150, self.screen_height//2 - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # Draw buttons side by side
        button_width = 200
        button_height = 80
        button_spacing = 50
        total_width = button_width * 2 + button_spacing
        start_x = self.screen_width//2 - total_width//2
        
        # Recalibrate button
        recalibrate_rect = (start_x, self.screen_height//2 + 50, button_width, button_height)
        cv2.rectangle(overlay, 
                     (recalibrate_rect[0], recalibrate_rect[1]),
                     (recalibrate_rect[0] + recalibrate_rect[2], recalibrate_rect[1] + recalibrate_rect[3]),
                     (0, 255, 0), -1)
        cv2.putText(overlay, "Recalibrate",
                   (recalibrate_rect[0] + 30, recalibrate_rect[1] + 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Continue button
        continue_rect = (start_x + button_width + button_spacing, self.screen_height//2 + 50, button_width, button_height)
        cv2.rectangle(overlay,
                     (continue_rect[0], continue_rect[1]),
                     (continue_rect[0] + continue_rect[2], continue_rect[1] + continue_rect[3]),
                     (0, 165, 255), -1)  # Orange color
        cv2.putText(overlay, "Continue",
                   (continue_rect[0] + 40, continue_rect[1] + 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Draw instructions
        cv2.putText(overlay, "Click 'Recalibrate' to try again or 'Continue' to proceed",
                   (self.screen_width//2 - 300, self.screen_height//2 + 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Apply overlay with transparency
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        return recalibrate_rect, continue_rect

    def draw_calibration_complete(self, frame):
        """Draw the calibration complete screen with Calculate Accuracy button."""
        # Create a semi-transparent overlay
        overlay = frame.copy()
        
        # Draw completion message
        msg = "Calibration Complete!"
        cv2.putText(overlay, msg,
                   (self.screen_width//2 - 200, self.screen_height//2 - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # Draw Calculate Accuracy button
        button_width = 300
        button_height = 80
        button_x = self.screen_width//2 - button_width//2
        button_y = self.screen_height//2 + 50
        
        cv2.rectangle(overlay,
                     (button_x, button_y),
                     (button_x + button_width, button_y + button_height),
                     (0, 165, 255), -1)  # Orange color
        cv2.putText(overlay, "Calculate Accuracy",
                   (button_x + 40, button_y + 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Draw instructions
        cv2.putText(overlay, "Click 'Calculate Accuracy' when ready to start the accuracy test",
                   (self.screen_width//2 - 350, self.screen_height//2 + 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Apply overlay with transparency
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        return (button_x, button_y, button_width, button_height)

    def start_calibration(self):
        """Start the calibration process."""
        self.calibrating = True
        self.current_point = 0
        self.clicks = 0
        self.ridge_regression.clear_data()
        self.kalman_filter.reset()
    
    def finish_calibration(self):
        """Finish calibration and show completion screen."""
        self.calibrating = False
        self.ridge_regression.train()
        print("Calibration complete! Click 'Calculate Accuracy' when ready.")
        self.showing_calibration_complete = True
    
    def run(self):
        """Run the eye tracking demo."""
        cap = cv2.VideoCapture(0)
        
        # Set up mouse callback
        cv2.setMouseCallback(self.window_name, lambda event, x, y, flags, param: 
                           self.handle_click(x, y) if event == cv2.EVENT_LBUTTONDOWN else None)
        
        print("Press 'c' to start calibration")
        print("Press 'q' to quit")
        
        # Create a blank frame to initialize the window
        blank_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        cv2.imshow(self.window_name, blank_frame)
        cv2.waitKey(100)  # Wait a bit for window to be created
        
        # Update window dimensions after window is displayed
        self.update_window_dimensions()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Mirror the frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Resize frame to match window dimensions
            frame = cv2.resize(frame, (self.screen_width, self.screen_height))
            
            # Store current frame for calibration
            self.current_frame = frame.copy()
            
            # Get eye features
            eye_features = self.face_detector.get_eye_features(frame)
            
            if eye_features is not None:
                # Get prediction
                prediction = self.ridge_regression.predict(eye_features)
                
                if prediction:
                    if self.testing_accuracy:
                        # During accuracy test, collect predictions
                        elapsed = cv2.getTickCount() / cv2.getTickFrequency() - self.accuracy_start_time
                        if elapsed < self.test_duration:
                            self.accuracy_predictions.append(prediction)
                        else:
                            # Calculate and display accuracy
                            self.accuracy_result = self.calculate_accuracy(self.accuracy_predictions, self.test_target)
                            print(f"\nAccuracy test complete!")
                            print(f"Your accuracy is: {self.accuracy_result}%")
                            self.testing_accuracy = False
                            self.showing_results = True
                    elif not self.calibrating and not self.showing_results and not self.showing_calibration_complete:
                        # Normal prediction mode
                        filtered_pred = self.kalman_filter.update([prediction['x'], prediction['y']])
                        x = max(0, min(int(filtered_pred[0]), self.screen_width - 1))
                        y = max(0, min(int(filtered_pred[1]), self.screen_height - 1))
                        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            # Draw appropriate UI based on current state
            if self.calibrating:
                self.draw_calibration_point(frame)
            elif self.testing_accuracy:
                self.draw_accuracy_test(frame)
            elif self.showing_results:
                self.draw_results(frame)
            elif self.showing_calibration_complete:
                self.draw_calibration_complete(frame)
            
            # Show frame
            cv2.imshow(self.window_name, frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c') and not self.calibrating and not self.testing_accuracy and not self.showing_results and not self.showing_calibration_complete:
                self.start_calibration()
        
        cap.release()
        cv2.destroyAllWindows()

    def handle_click(self, x, y):
        """Handle mouse click for calibration and various buttons."""
        if self.showing_calibration_complete:
            # Calculate button position
            button_width = 300
            button_height = 80
            button_x = self.screen_width//2 - button_width//2
            button_y = self.screen_height//2 + 50
            
            # Check if click is on Calculate Accuracy button
            if (button_x <= x <= button_x + button_width and
                button_y <= y <= button_y + button_height):
                self.showing_calibration_complete = False
                self.start_accuracy_test()
                return
                
        elif self.showing_results:
            # Calculate button positions
            button_width = 200
            button_height = 80
            button_spacing = 50
            total_width = button_width * 2 + button_spacing
            start_x = self.screen_width//2 - total_width//2
            
            # Recalibrate button
            recalibrate_rect = (start_x, self.screen_height//2 + 50, button_width, button_height)
            # Continue button
            continue_rect = (start_x + button_width + button_spacing, self.screen_height//2 + 50, button_width, button_height)
            
            # Check if click is on recalibrate button
            if (recalibrate_rect[0] <= x <= recalibrate_rect[0] + recalibrate_rect[2] and
                recalibrate_rect[1] <= y <= recalibrate_rect[1] + recalibrate_rect[3]):
                self.showing_results = False
                self.start_calibration()
                return
                
            # Check if click is on continue button
            if (continue_rect[0] <= x <= continue_rect[0] + continue_rect[2] and
                continue_rect[1] <= y <= continue_rect[1] + continue_rect[3]):
                self.showing_results = False
                print("\nStarting eye tracking...")
                return
                
        if not self.calibrating:
            return
            
        if self.current_point < len(self.calibration_points):
            target_x, target_y = self.calibration_points[self.current_point]
            # Check if click is near the calibration point
            if abs(x - target_x) < 20 and abs(y - target_y) < 20:
                # Get current eye features
                eye_features = self.face_detector.get_eye_features(self.current_frame)
                if eye_features is not None:
                    # Add data point to ridge regression model
                    self.ridge_regression.add_data_point(eye_features, (target_x, target_y), 'click')
                    self.clicks += 1
                    if self.clicks >= self.clicks_per_point:
                        self.current_point += 1
                        self.clicks = 0
                        if self.current_point >= len(self.calibration_points):
                            self.finish_calibration()

if __name__ == "__main__":
    demo = CalibrationDemo()
    demo.run() 