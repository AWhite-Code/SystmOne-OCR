from capture.selection_window import SelectionWindow
from capture.capture_window import CaptureWindow
from ocr.image_processor import ImageProcessor
from ocr.text_processor import TextProcessor
from config import TESSERACT_PATH
import pyperclip

class ScreenCaptureOCR:
    def __init__(self):
        # Initialize our processing components
        self.image_processor = ImageProcessor(TESSERACT_PATH)
        self.text_processor = TextProcessor()
        self.capture_window = CaptureWindow()
        
        # Get dimensions from capture window
        total_width, total_height, min_x, min_y = self.capture_window.get_screen_dimensions()
        dimensions = (total_width, total_height, min_x, min_y)
        
        # Initialize selection window
        self.selection_window = SelectionWindow(
            dimensions=dimensions,
            on_selection_complete=self._handle_selection
        )

    def _handle_selection(self, bbox):
        """Handle the completion of area selection."""
        x1, y1, x2, y2 = bbox
        print(f"Capturing area: ({x1}, {y1}) to ({x2}, {y2})")
            
        try:
            # Take screenshot
            screenshot = self.capture_window.capture_screen((x1, y1, x2, y2))
            
            # Use ImageProcessor for OCR
            processed_image = self.image_processor.preprocess_image(screenshot)
            raw_text = self.image_processor.perform_ocr(processed_image)
            
            # Process and clean up the text
            text = self.text_processor.process_text(raw_text)
            
            # Copy to clipboard
            pyperclip.copy(text.strip())
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise e
        finally:
            # Quit application
            self.selection_window.quit()

    def run(self):
        """Start the application."""
        self.selection_window.start()

def main():
    app = ScreenCaptureOCR()
    app.run()

if __name__ == "__main__":
    main()