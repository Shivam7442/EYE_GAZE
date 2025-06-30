import tkinter as tk
import logging

class CursorManager:
    def __init__(self, root):
        self.root = root
        self.cursor_window = None
        self.cursor_canvas = None
        self.cursor_id = None
        self.cursor_canvas_ready = False
        self.cursor_size = 40  # Increased cursor size
        self.init_cursor()

    def init_cursor(self):
        """Initialize a transparent Toplevel window with a small cursor canvas."""
        logging.info("Starting cursor initialization")
        try:
            # Create a Toplevel window for the cursor
            self.cursor_window = tk.Toplevel(self.root)
            self.cursor_window.overrideredirect(True)  # Remove window decorations
            self.cursor_window.attributes('-topmost', True)  # Keep on top
            self.cursor_window.attributes('-transparentcolor', 'black')  # Make black transparent
            self.cursor_window.configure(bg='black')

            # Create a canvas that matches the cursor size
            self.cursor_canvas = tk.Canvas(
                self.cursor_window,
                highlightthickness=0,
                bg='black',  # Background will be transparent
                width=self.cursor_size,
                height=self.cursor_size
            )
            self.cursor_canvas.pack()

            # Create the cursor (changed to green)
            self.cursor_id = self.cursor_canvas.create_oval(
                0, 0, self.cursor_size, self.cursor_size,
                fill='gray',  # Changed color to green
                outline='green',
                width=4
            )
            self.cursor_canvas.itemconfig(self.cursor_id, state='hidden')

            # Initially position the window off-screen
            self.cursor_window.geometry(f"{self.cursor_size}x{self.cursor_size}+0+0")

            self.cursor_canvas_ready = True
            logging.info("Cursor initialized successfully")

        except Exception as e:
            logging.error(f"Error initializing cursor: {str(e)}")
            self.cursor_canvas_ready = False
            raise

    def update_canvas_size(self):
        """No longer needed, as the canvas size is fixed to the cursor size."""
        pass

    def on_window_resize(self, event):
        """No resizing needed for the cursor window."""
        pass

    def show_cursor(self):
        """Show the cursor by making the window visible."""
        try:
            self.cursor_canvas.itemconfig(self.cursor_id, state='normal')
            logging.info("Cursor shown")
        except Exception as e:
            logging.error(f"Error showing cursor: {str(e)}")

    def hide_cursor(self):
        """Hide the cursor by hiding the window."""
        try:
            self.cursor_canvas.itemconfig(self.cursor_id, state='hidden')
            logging.info("Cursor hidden")
        except Exception as e:
            logging.error(f"Error hiding cursor: {str(e)}")

    def move_cursor(self, x, y):
        """Move the cursor window to the specified (x, y) position."""
        try:
            # Adjust the position so the cursor's center is at (x, y)
            adjusted_x = x - self.cursor_size // 2
            adjusted_y = y - self.cursor_size // 2
            self.cursor_window.geometry(f"{self.cursor_size}x{self.cursor_size}+{adjusted_x}+{adjusted_y}")
            logging.debug(f"Cursor moved to ({x}, {y})")
        except Exception as e:
            logging.error(f"Error moving cursor: {str(e)}")

    def get_cursor_canvas(self):
        """Return the cursor canvas for external use."""
        return self.cursor_canvas

    def get_cursor_id(self):
        """Return the cursor ID for external use."""
        return self.cursor_id

    def is_cursor_canvas_ready(self):
        """Return whether the cursor canvas is ready."""
        return self.cursor_canvas_ready