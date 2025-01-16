import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
from typing import List, Tuple

class CaptureWindow:
    def __init__(self):
        # Get information about all monitors
        self.monitors = win32api.EnumDisplayMonitors()
        self.monitor_info = self._get_monitor_info()
        
        # Calculate total screen dimensions
        self.total_dimensions = self._calculate_screen_dimensions()

    def _get_monitor_info(self) -> List[dict]:
        """Get information about all connected monitors."""
        monitor_info = []
        for monitor in self.monitors:
            info = win32api.GetMonitorInfo(monitor[0])
            monitor_info.append(info)
            print(f"Monitor info: {info}")
        return monitor_info

    def _calculate_screen_dimensions(self) -> Tuple[int, int, int, int]:
        """Calculate total dimensions across all monitors."""
        monitor_rects = [info['Monitor'] for info in self.monitor_info]
        total_width = max(rect[2] for rect in monitor_rects)
        total_height = max(rect[3] for rect in monitor_rects)
        min_x = min(rect[0] for rect in monitor_rects)
        min_y = min(rect[1] for rect in monitor_rects)
        
        return total_width, total_height, min_x, min_y

    def get_screen_dimensions(self) -> Tuple[int, int, int, int]:
        """Return the total screen dimensions."""
        return self.total_dimensions

    def capture_screen(self, bbox: Tuple[int, int, int, int]) -> Image.Image:
        """
        Capture a portion of the screen.
        
        Args:
            bbox: Tuple of (x1, y1, x2, y2) coordinates
            
        Returns:
            PIL Image of the captured area
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Create device context
        hwnd = win32gui.GetDesktopWindow()
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        try:
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Copy screen to bitmap
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (x1, y1), win32con.SRCCOPY)
            
            # Convert to PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            
            return img
            
        finally:
            # Clean up
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            win32gui.DeleteObject(saveBitMap.GetHandle())