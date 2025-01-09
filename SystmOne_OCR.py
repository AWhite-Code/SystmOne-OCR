import tkinter as tk
import pytesseract
import pyperclip
import win32gui
import win32ui
import win32con
import win32api
import re
from PIL import Image, ImageEnhance, ImageOps

# Set Tesseract path
TESSERACT_PATH = r'C:\Users\Alexwh\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

class ScreenCaptureOCR:
    def __init__(self):
        # Get information about all monitors
        monitors = win32api.EnumDisplayMonitors()
        self.monitor_info = []
        
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
                
                # Preprocess the image
                processed_image = self.preprocess_image(screenshot)
                
                # Perform OCR with custom configuration
                custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
                raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
                
                # Process and clean up the text
                text = self.process_text(raw_text)
                
                # Copy to clipboard
                pyperclip.copy(text.strip())
                # Copy to clipboard
                pyperclip.copy(text.strip())
                
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                raise e
            finally:
                # Quit application
                self.root.quit()
    
    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy for blue text.
        """
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Scale up first to avoid losing detail
        scaled = image.resize((image.width * 3, image.height * 3), Image.LANCZOS)
        
        # Convert to grayscale
        gray = ImageOps.grayscale(scaled)
        
        # Increase contrast
        contrast = ImageEnhance.Contrast(gray).enhance(3.0)
        
        # Slightly increase brightness to make text clearer
        brightness = ImageEnhance.Brightness(contrast).enhance(1.1)
        
        # Add padding around the image to help with character recognition
        padded = ImageOps.expand(brightness, border=20, fill=255)
        
        # Save debug image
        padded.save('debug_ocr.png')
        
        return padded
        
    def format_date(self, text):
        """
        Ensure proper spacing in dates while preserving other text.
        """
        # List of month abbreviations
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create regex pattern for dates
        # Matches: 1-2 digits + optional space + month + optional space + 4 digits
        pattern = r'(\d{1,2})\s*(' + '|'.join(months) + r')\s*(\d{4})'
        
        def repl(match):
            day, month, year = match.groups()
            # Ensure day is padded with leading zero if needed
            return f"{day.zfill(2)} {month} {year}"
            
        return re.sub(pattern, repl, text)

    def process_text(self, text):
        """
        Clean up OCR output specifically for read codes from SystmOne.
        Format: DD MMM YYYY Description (CODE)
        """
        # Replace any zero-width spaces or other invisible characters
        text = text.replace('\u200b', ' ').replace('\n', ' ')
        
        # Clean up multiple spaces
        text = ' '.join(text.split())
        
        # Format dates properly
        text = self.format_date(text)
        
        # Split by opening bracket to separate different codes
        parts = text.split('(')
        
        formatted_codes = []
        for i, part in enumerate(parts):
            if i == 0:  # First part might not have a closing bracket
                if part.strip():  # Only add if not empty
                    formatted_codes.append(part.strip())
            else:
                # Find the closing bracket
                code_parts = part.split(')')
                if len(code_parts) >= 2:
                    # Reconstruct with proper spacing
                    code = f"({code_parts[0]})"
                    
                    # Add to previous line if it exists, otherwise start new line
                    if formatted_codes:
                        formatted_codes[-1] = formatted_codes[-1] + " " + code
                    else:
                        formatted_codes.append(code)
                    
                    # Add remaining text as new line if it exists
                    remaining = ')'.join(code_parts[1:]).strip()
                    if remaining:
                        formatted_codes.append(remaining)
        
        # Join with newlines
        return '\n'.join(formatted_codes)

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

def main():
    app = ScreenCaptureOCR()
    app.root.mainloop()

if __name__ == "__main__":
    main()