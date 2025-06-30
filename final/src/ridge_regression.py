import numpy as np
from scipy import linalg
from .data_window import DataWindow

class RidgeRegression:
    """
    Ridge Regression implementation for gaze prediction.
    Similar to WebGazer's ridge regression implementation.
    """
    def __init__(self, ridge_param=1e-5):
        """
        Initialize the ridge regression model.
        
        Args:
            ridge_param (float): Ridge parameter (lambda) for regularization
        """
        self.ridge_param = ridge_param
        self.coefficients_x = None
        self.coefficients_y = None
        self.data_window = DataWindow(50)
        self.trail_window = DataWindow(10)  # For storing recent gaze points
        
    def fit(self, X, y_x, y_y):
        """
        Fit the ridge regression model.
        
        Args:
            X (np.ndarray): Feature matrix
            y_x (np.ndarray): X-coordinate targets
            y_y (np.ndarray): Y-coordinate targets
        """
        # Add ridge parameter to diagonal
        XtX = np.dot(X.T, X)
        XtX[np.diag_indices_from(XtX)] += self.ridge_param
        
        try:
            # Solve for coefficients
            self.coefficients_x = np.linalg.solve(XtX, np.dot(X.T, y_x))
            self.coefficients_y = np.linalg.solve(XtX, np.dot(X.T, y_y))
        except np.linalg.LinAlgError:
            # If matrix is singular, increase ridge parameter and try again
            self.ridge_param *= 10
            self.fit(X, y_x, y_y)
    
    def predict(self, X):
        """
        Predict gaze coordinates.
        
        Args:
            X (np.ndarray): Feature matrix for prediction
            
        Returns:
            dict: Predicted x and y coordinates
        """
        if self.coefficients_x is None or self.coefficients_y is None:
            return None
            
        return {
            'x': float(np.dot(X, self.coefficients_x)),
            'y': float(np.dot(X, self.coefficients_y))
        }
    
    def add_data_point(self, eye_features, screen_pos, data_type='click'):
        """
        Add a new data point for training.
        
        Args:
            eye_features (np.ndarray): Eye feature vector
            screen_pos (tuple): (x, y) screen coordinates
            data_type (str): Type of data point ('click' or 'move')
        """
        data = {
            'eye_features': eye_features,
            'screen_pos': screen_pos,
            'type': data_type
        }
        
        if data_type == 'click':
            self.data_window.push(data)
        else:  # move
            self.trail_window.push(data)
    
    def get_training_data(self):
        """
        Get all data points for training.
        
        Returns:
            tuple: (X, y_x, y_y) training data
        """
        all_data = self.data_window.get_all() + self.trail_window.get_all()
        
        if not all_data:
            return None, None, None
            
        X = np.array([d['eye_features'] for d in all_data])
        y_x = np.array([d['screen_pos'][0] for d in all_data])
        y_y = np.array([d['screen_pos'][1] for d in all_data])
        
        return X, y_x, y_y
    
    def train(self):
        """Train the model using all available data points."""
        X, y_x, y_y = self.get_training_data()
        if X is not None:
            self.fit(X, y_x, y_y)
    
    def clear_data(self):
        """Clear all stored data points."""
        self.data_window.clear()
        self.trail_window.clear()
        self.coefficients_x = None
        self.coefficients_y = None 