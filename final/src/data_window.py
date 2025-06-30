from collections import deque
import time

class DataWindow:
    """
    A circular buffer implementation for storing eye tracking data points.
    Similar to WebGazer's DataWindow implementation.
    """
    def __init__(self, window_size=50):
        """
        Initialize the data window with a fixed size.
        
        Args:
            window_size (int): Maximum number of data points to store
        """
        self.window_size = window_size
        self.data = deque(maxlen=window_size)
        self.times = deque(maxlen=window_size)
    
    def push(self, data, timestamp=None):
        """
        Add a new data point to the window.
        
        Args:
            data: The data point to store
            timestamp: Optional timestamp, defaults to current time
        """
        if timestamp is None:
            timestamp = time.time()
        self.data.append(data)
        self.times.append(timestamp)
    
    def get(self, index):
        """
        Get a data point at the specified index.
        
        Args:
            index (int): Index of the data point to retrieve
            
        Returns:
            The data point at the specified index
        """
        return self.data[index]
    
    def get_all(self):
        """
        Get all stored data points.
        
        Returns:
            list: All stored data points
        """
        return list(self.data)
    
    def get_times(self):
        """
        Get all stored timestamps.
        
        Returns:
            list: All stored timestamps
        """
        return list(self.times)
    
    def clear(self):
        """Clear all stored data points and timestamps."""
        self.data.clear()
        self.times.clear()
    
    def __len__(self):
        """Return the number of stored data points."""
        return len(self.data)
    
    def is_full(self):
        """Check if the window is full."""
        return len(self.data) == self.window_size 