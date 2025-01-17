# controllers/ocr_controller.py
import pyperclip
from PIL import Image
from typing import Tuple


class OCRController:
    def __init__(self, image_processor, text_processor, capture_window):
        self.image_processor = image_processor
        self.text_processor = text_processor
        self.capture_window = capture_window

    def handle_selection(self, bbox: Tuple[float, float, float, float]) -> str:
        """
        Handle the completion of area selection.

        Args:
            bbox: Tuple of (x1, y1, x2, y2) coordinates

        Returns:
            Processed text from the selected area
        """
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

            return text.strip()

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise
