# main.py
from capture.selection_window import SelectionWindow
from capture.capture_window import CaptureWindow
from ocr.image_processor import ImageProcessor
from ocr.text_processor import TextProcessor
from controllers.ocr_controller import OCRController
from config import TESSERACT_PATH
from gui.window import create_window


class ScreenCaptureOCR:
    def __init__(self):
        # Initialize components
        self.image_processor = ImageProcessor(TESSERACT_PATH)
        self.text_processor = TextProcessor()
        self.capture_window = CaptureWindow()

        # Initialize controller
        self.controller = OCRController(
            self.image_processor, self.text_processor, self.capture_window
        )

        # Get dimensions from capture window
        total_width, total_height, min_x, min_y = (
            self.capture_window.get_screen_dimensions()
        )
        dimensions = (total_width, total_height, min_x, min_y)

        # Initialize selection window with controller
        self.selection_window = SelectionWindow(
            dimensions=dimensions, on_selection_complete=self._on_selection_complete
        )

        # Initialize GUI window
        self.window = create_window()

    def _on_selection_complete(self, bbox):
        """Simple wrapper to call controller and quit selection window."""
        try:
            self.controller.handle_selection(bbox)
        finally:
            self.selection_window.quit()

    def run(self):
        """Start the application."""
        self.selection_window.start()


def main():
    app = ScreenCaptureOCR()
    app.run()


if __name__ == "__main__":
    main()
