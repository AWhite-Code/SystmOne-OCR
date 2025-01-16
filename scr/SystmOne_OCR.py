import tkinter as tk
import pytesseract
import pyperclip
import win32gui
import win32ui
import win32con
import win32api
import re
from PIL import Image, ImageOps, ImageEnhance
from ocr.image_processor import ImageProcessor
from config import TESSERACT_PATH, OVERLAY_ALPHA, SELECTION_BORDER_COLOR, SELECTION_BORDER_WIDTH

# Set Tesseract path
TESSERACT_PATH = r'vendor/tesseract/tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class ScreenCaptureOCR:
    def __init__(self):
        # Get information about all monitors
        monitors = win32api.EnumDisplayMonitors()
        self.monitor_info = []
        self.image_processor = ImageProcessor(TESSERACT_PATH)
        
        for monitor in monitors:
            info = win32api.GetMonitorInfo(monitor[0])
            self.monitor_info.append(info)
            print(f"Monitor info: {info}")
        
        # Calculate total dimensions
        monitor_rects = [info['Monitor'] for info in self.monitor_info]
        self.total_width = max(rect[2] for rect in monitor_rects)
        self.total_height = max(rect[3] for rect in monitor_rects)
        self.min_x = min(rect[0] for rect in monitor_rects)
        self.min_y = min(rect[1] for rect in monitor_rects)
        
        # Create main window for the dark overlay
        self.root = tk.Tk()
        self.root.title("Screen Capture OCR")
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.3)
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
        
        # Create separate window for the selection rectangle
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.overrideredirect(True)
        self.selection_window.attributes('-alpha', 1.0)  # Fully opaque
        self.selection_window.attributes('-topmost', True)
        self.selection_window.geometry(f"{self.total_width}x{self.total_height}+{self.min_x}+{self.min_y}")
        
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
        
        # Initialize variables
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.clear_area = None
        self.original_alpha = 0.3
        
        # Bind events to main canvas
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.quit())
        
    def on_press(self, event):
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
        
        # Create the selection rectangle with thick red border on the selection canvas
        self.current_rect = self.selection_canvas.create_rectangle(
            self.canvas_start_x, self.canvas_start_y,
            self.canvas_start_x, self.canvas_start_y,
            outline='#FF0000',
            width=6
        )
        
        # Create the clear area rectangle on the main canvas
        self.clear_area = self.canvas.create_rectangle(
            self.canvas_start_x, self.canvas_start_y,
            self.canvas_start_x, self.canvas_start_y,
            fill='white',
            stipple='gray50'
        )
        
        # Make the window more transparent while drawing
        self.root.attributes('-alpha', 0.1)
    
    def on_drag(self, event):
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
    
    def on_release(self, event):
        if self.start_x is not None and self.start_y is not None:
            # Restore original transparency before capture
            self.root.attributes('-alpha', self.original_alpha)
            
            # Calculate screen coordinates
            end_x = self.root.winfo_x() + event.x
            end_y = self.root.winfo_y() + event.y
            
            x1 = min(self.start_x, end_x)
            y1 = min(self.start_y, end_y)
            x2 = max(self.start_x, end_x)
            y2 = max(self.start_y, end_y)
            
            print(f"Capturing area: ({x1}, {y1}) to ({x2}, {y2})")
            
            # Hide windows for clean screenshot
            self.root.withdraw()
            self.selection_window.withdraw()
            
            try:
                # Take screenshot
                screenshot = self.capture_screen((x1, y1, x2, y2))
                
                # Use ImageProcessor for OCR
                processed_image = self.image_processor.preprocess_image(screenshot)
                raw_text = self.image_processor.perform_ocr(processed_image)
                
                # Process and clean up the text
                text = self.process_text(raw_text)
                
                # Copy to clipboard
                pyperclip.copy(text.strip())
                
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                raise e
            finally:
                # Quit application
                self.root.quit()

    def capture_screen(self, bbox):
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Create device context
        hwnd = win32gui.GetDesktopWindow()
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
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
        
        # Clean up
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        
        return img
       
    def format_date(self, text):
        """
        Handles various date formats found in medical records:
        - Full dates: DD MMM YYYY (e.g., 26 May 1959)
        - Month-year: MMM YYYY (e.g., Oct 1999)
        - Year only: YYYY (e.g., 1975)
        """
        # List of month abbreviations
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Pattern for full dates (day + month + year)
        full_date = r'(\d{1,2})\s*(' + '|'.join(months) + r')\s*(\d{4})'
        
        # Pattern for month-year only
        month_year = r'\b(' + '|'.join(months) + r')\s*(\d{4})\b'
        
        def format_full_date(match):
            day, month, year = match.groups()
            return f"{day.zfill(2)} {month} {year}"
            
        def format_month_year(match):
            month, year = match.groups()
            return f"{month} {year}"
        
        # Apply patterns in order: full dates, then month-year
        # Year-only dates are left as is since they don't need formatting
        text = re.sub(full_date, format_full_date, text)
        text = re.sub(month_year, format_month_year, text)
        
        return text

    def remove_read_codes(self, text):
        """
        Removes medical read codes from text, handling various OCR artifacts.
        
        Handles these code formats:
        - Standard format: (A55.)
        - Without parentheses: XE0r9
        - With Yen symbol: ¥3306
        - With dots: 7F19.
        - Multiple closing parentheses: X407Z))
        """
        # Normalize any Yen symbols to Y because my OCR is funky
        text = text.replace('¥', 'Y')
        
        # Patterns to remove, in order of specificity
        patterns = [
            r'\s*\([A-Z0-9._]+\)+\s*$',     # (XE123), (X407Z))
            r'\s+[A-Z][A-Z0-9._]+\)+\s*$',  # X407Z))
            r'\s+[A-Z][A-Z0-9._]+\s*$',     # M1612
            r'\s+[0-9][A-Z0-9]+\.[0-9]*\s*$', # 7F19.
            r'\s*[.()]+\s*$'                 # Cleanup trailing dots/parentheses
        ]
        
        # Apply each pattern in sequence
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        
        return text.strip()

    def clean_description(self, text):
        """
        Cleans OCR artifacts while preserving important text structure.
        Handles various OCR-specific issues like missing spaces and special characters.
        """
        # Fix common OCR date formatting issues
        months = "(?:Oct|Dec|Feb|Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Nov)"
        text = re.sub(f'(\d+)({months})', r'\1 \2', text)
        
        # Remove various OCR artifacts while preserving structure
        replacements = [
            (r'[_~]', ''),                    # Remove underscores and tildes
            (r'\[(?:Dj|D|X|Xj)\]', ''),       # Remove [D], [Dj], [X], [Xj]
            (r'={1,2}\[(?:Xj|X)\]', ''),      # Remove =[X], =[Xj]
            (r'(?:—|-)+\s*', ''),             # Remove em dashes and hyphens
            (r'=+\s*', ''),                   # Remove equals signs
            (r'NOS\s*\(', 'NOS '),            # Handle "NOS(" properly
            (r'\s+', ' ')                     # Normalize spaces
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        
        return text.strip()

    def process_text(self, text):
        """
        Main processing function that handles OCR output formatting.
        Ensures proper handling of dates, descriptions, and removal of read codes.
        """
        # Initial cleanup of zero-width spaces
        text = text.replace('\u200b', ' ')
        
        # Split into lines and process each line
        lines = text.split('\n')
        formatted_entries = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Clean up the line and format dates
            line = self.clean_description(line)
            line = self.format_date(line)
            line = self.remove_read_codes(line)
            
            if line.strip():
                formatted_entries.append(line)
        
        # Handle duplicates by date and description
        def extract_date_and_description(entry):
            """Helper function to parse entry into date and description components."""
            parts = entry.split()
            
            # Full date (DD MMM YYYY)
            if len(parts) >= 3 and parts[1] in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                return ' '.join(parts[:3]), ' '.join(parts[3:])
            
            # Month Year only
            elif len(parts) >= 2 and parts[0] in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                return ' '.join(parts[:2]), ' '.join(parts[2:])
            
            # Year only
            elif parts and parts[0].isdigit() and len(parts[0]) == 4:
                return parts[0], ' '.join(parts[1:])
            
            return None, None

        # Keep track of unique entries by date+description
        seen_entries = set()
        filtered_entries = []
        
        for entry in formatted_entries:
            date, description = extract_date_and_description(entry)
            if date is None:
                filtered_entries.append(entry)
                continue
                
            entry_key = f"{date}|{description}"
            if entry_key not in seen_entries:
                seen_entries.add(entry_key)
                filtered_entries.append(entry)
        
        return '\n'.join(filtered_entries)

def main():
    app = ScreenCaptureOCR()
    app.root.mainloop()

if __name__ == "__main__":
    main()