import tkinter as tk
import time
import logging

class DwellTimer:
    def __init__(self, root, dwell_callback, dwell_time=1.0):
        """Initialize the DwellTimer.

        Args:
            root: Tkinter root window.
            dwell_callback: Function to call on dwell completion (receives x, y).
            dwell_time: Time (seconds) to dwell before triggering callback.
        """
        self.root = root
        self.dwell_callback = dwell_callback
        self.dwell_time = dwell_time
        self.current_pos = None
        self.start_time = None
        self.is_active = False
        logging.info("DwellTimer initialized")

    def set_dwell_time(self, dwell_time):
        """Update the dwell time."""
        self.dwell_time = float(dwell_time)
        logging.debug(f"Dwell time set to {self.dwell_time} seconds")

    def update_position(self, x, y):
        """Update gaze position and check for dwell."""
        if not self.is_active:
            self.current_pos = (x, y)
            self.start_time = time.time()
            self.is_active = True
            return

        # Check if gaze has moved significantly
        if self.current_pos and abs(x - self.current_pos[0]) < 20 and abs(y - self.current_pos[1]) < 20:
            # Still within dwell range
            if time.time() - self.start_time >= self.dwell_time:
                # Dwell time reached, trigger callback
                self.dwell_callback(x, y)
                self.reset()
        else:
            # Reset if moved out of range
            self.reset()
            self.current_pos = (x, y)
            self.start_time = time.time()
            self.is_active = True

    def reset(self):
        """Reset the dwell timer."""
        self.current_pos = None
        self.start_time = None
        self.is_active = False