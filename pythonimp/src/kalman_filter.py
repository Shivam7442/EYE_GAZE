import numpy as np

class KalmanFilter:
    """
    Kalman Filter implementation for smoothing gaze predictions.
    Similar to WebGazer's Kalman filter implementation.
    """
    def __init__(self):
        # State transition matrix (4x4)
        # [x, y, dx, dy] where dx, dy are velocities
        self.F = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Measurement matrix (2x4)
        # We only measure x and y positions
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        
        # Process noise (4x4)
        # Adjusts how much we trust the model
        self.Q = np.array([
            [1/4, 0, 1/2, 0],
            [0, 1/4, 0, 1/2],
            [1/2, 0, 1, 0],
            [0, 1/2, 0, 1]
        ]) * (1/10)  # delta_t
        
        # Measurement noise (2x2)
        # Adjusts how much we trust the measurements
        self.R = np.eye(2) * 47  # pixel_error
        
        # Initial state [x, y, dx, dy]
        self.x = np.array([[500], [500], [0], [0]])
        
        # Initial covariance matrix
        self.P = np.eye(4) * 0.0001
    
    def update(self, measurement):
        """
        Update the Kalman filter with a new measurement.
        
        Args:
            measurement (np.ndarray): New measurement [x, y]
            
        Returns:
            np.ndarray: Filtered measurement [x, y]
        """
        # Convert measurement to column vector
        z = np.array(measurement).reshape(2, 1)
        
        # Prediction step
        x_pred = np.dot(self.F, self.x)
        P_pred = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q
        
        # Update step
        y = z - np.dot(self.H, x_pred)  # Innovation
        S = np.dot(np.dot(self.H, P_pred), self.H.T) + self.R  # Innovation covariance
        K = np.dot(np.dot(P_pred, self.H.T), np.linalg.inv(S))  # Kalman gain
        
        # Correction
        self.x = x_pred + np.dot(K, y)
        self.P = np.dot(np.eye(4) - np.dot(K, self.H), P_pred)
        
        # Return filtered measurement
        return np.dot(self.H, self.x).flatten()
    
    def reset(self):
        """Reset the filter to initial state."""
        self.x = np.array([[500], [500], [0], [0]])
        self.P = np.eye(4) * 0.0001 