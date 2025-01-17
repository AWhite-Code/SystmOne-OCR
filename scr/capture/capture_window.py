import mss
import mss.tools
from PIL import Image
from typing import List, Tuple


class CaptureWindow:
    def __init__(self):
        self.sct = mss.mss()
        # Calculate total screen dimensions
        self.total_dimensions = self._calculate_screen_dimensions()

    def _calculate_screen_dimensions(self) -> Tuple[int, int, int, int]:
        """Calculate total dimensions across all monitors."""
        monitors = self.sct.monitors[1:]  # Skip the "all monitors" monitor
        if not monitors:
            # Fallback to primary monitor if no other monitors found
            monitor = self.sct.monitors[0]
            return (monitor["width"], monitor["height"], 0, 0)

        total_width = max(m["left"] + m["width"] for m in monitors)
        total_height = max(m["top"] + m["height"] for m in monitors)
        min_x = min(m["left"] for m in monitors)
        min_y = min(m["top"] for m in monitors)

        return total_width, total_height, min_x, min_y

    def get_screen_dimensions(self) -> Tuple[int, int, int, int]:
        """Return the total screen dimensions."""
        return self.total_dimensions

    def capture_screen(self, bbox: Tuple[float, float, float, float]) -> Image.Image:
        """
        Capture a portion of the screen.

        Args:
            bbox: Tuple of (x1, y1, x2, y2) coordinates

        Returns:
            PIL Image of the captured area
        """
        try:
            # Convert float coordinates to integers
            x1, y1, x2, y2 = map(int, bbox)

            # Create the region dict that mss expects
            region = {"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1}

            # Capture the screenshot
            screenshot = self.sct.grab(region)

            # Convert to PIL Image
            return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        except Exception as e:
            print(f"Screen capture error: {str(e)}")
            raise

    def __del__(self):
        """Cleanup the mss instance."""
        try:
            self.sct.close()
        except:
            pass
