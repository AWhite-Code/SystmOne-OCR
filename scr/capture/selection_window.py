import tkinter as tk
from typing import Tuple, Optional, Callable
from config import (
    OVERLAY_ALPHA,
    SELECTION_BORDER_COLOR,
    SELECTION_BORDER_WIDTH
)

class SelectionWindow:
    def __init__(self, dimensions: Tuple[int, int, int, int], on_selection_complete: Callable):
        """
        Initialize the selection window system.
        
        Args:
            dimensions: Tuple of (total_width, total_height, min_x, min_y)
            on_selection_complete: Callback function when selection is complete
        """
        self.total_width, self.total_height, self.min_x, self.min_y = dimensions
        self.on_selection_complete = on_selection_complete
        
        # Initialize state variables
        self.start_x: Optional[int] = None
        self.start_y: Optional[int] = None
        self.canvas_start_x: Optional[int] = None
        self.canvas_start_y: Optional[int] = None
        self.current_rect = None
        self.clear_area = None
        
        self._setup_main_window()
        self._setup_selection_window()
        self._bind_events()

    def _setup_main_window(self):
        """Set up the main dark overlay window."""
        self.root = tk.Tk()
        self.root.title("Screen Capture OCR")
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', OVERLAY_ALPHA)
        self.root.attributes('-topmost', True)
        
        # Position and size the window to cover all monitors
        self.root.geometry(f"{self.total_width}x{self.total_height}+{self.min_x}+{self.min_y}")
        
        # Create canvas for the dark overlay
        self.canvas = tk.Canvas(
            self.root,
            cursor="cross",
            width=self.total_width,
            height=self.total_height,
            highlightthickness=0,
            bg='black'
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _setup_selection_window(self):
        """Set up the transparent selection window."""
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.overrideredirect(True)
        self.selection_window.attributes('-alpha', 1.0)
        self.selection_window.attributes('-topmost', True)
        self.selection_window.geometry(
            f"{self.total_width}x{self.total_height}+{self.min_x}+{self.min_y}"
        )
        
        # Make selection window transparent and click-through
        self.selection_window.attributes('-transparentcolor', 'black')
        
        # Create canvas for the selection rectangle
        self.selection_canvas = tk.Canvas(
            self.selection_window,
            width=self.total_width,
            height=self.total_height,
            highlightthickness=0,
            bg='black'
        )
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self):
        """Bind mouse and keyboard events."""
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", lambda e: self.root.quit())

    def _on_press(self, event):
        """Handle mouse button press."""
        # Store both screen and canvas coordinates
        self.start_x = self.root.winfo_x() + event.x
        self.start_y = self.root.winfo_y() + event.y
        self.canvas_start_x = event.x
        self.canvas_start_y = event.y
        
        # Delete existing rectangles if any
        if self.current_rect:
            self.selection_canvas.delete(self.current_rect)
        if self.clear_area:
            self.canvas.delete(self.clear_area)
        
        # Create selection rectangle with configured appearance
        self.current_rect = self.selection_canvas.create_rectangle(
            self.canvas_start_x, self.canvas_start_y,
            self.canvas_start_x, self.canvas_start_y,
            outline=SELECTION_BORDER_COLOR,
            width=SELECTION_BORDER_WIDTH
        )
        
        # Create clear area in overlay
        self.clear_area = self.canvas.create_rectangle(
            self.canvas_start_x, self.canvas_start_y,
            self.canvas_start_x, self.canvas_start_y,
            fill='white',
            stipple='gray50'
        )
        
        # Make overlay more transparent while selecting
        self.root.attributes('-alpha', 0.1)

    def _on_drag(self, event):
        """Handle mouse drag."""
        if self.current_rect and self.clear_area:
            # Update both rectangles
            self.selection_canvas.coords(
                self.current_rect,
                self.canvas_start_x, self.canvas_start_y,
                event.x, event.y
            )
            self.canvas.coords(
                self.clear_area,
                self.canvas_start_x, self.canvas_start_y,
                event.x, event.y
            )

    def _on_release(self, event):
        """Handle mouse button release."""
        if self.start_x is not None and self.start_y is not None:
            # Calculate final coordinates
            end_x = self.root.winfo_x() + event.x
            end_y = self.root.winfo_y() + event.y
            
            x1 = min(self.start_x, end_x)
            y1 = min(self.start_y, end_y)
            x2 = max(self.start_x, end_x)
            y2 = max(self.start_y, end_y)
            
            # Hide windows for clean capture
            self.hide_windows()
            
            # Call the completion callback with coordinates
            self.on_selection_complete((x1, y1, x2, y2))

    def hide_windows(self):
        """Hide all windows."""
        self.root.withdraw()
        self.selection_window.withdraw()

    def show_windows(self):
        """Show all windows."""
        self.root.deiconify()
        self.selection_window.deiconify()

    def start(self):
        """Start the selection window system."""
        self.root.mainloop()

    def quit(self):
        """Quit the selection window system."""
        self.root.quit()