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
        self.dimensions = (total_width, total_height, min_x, min_y)

        # Initialize GUI window with reference to this class
        self.window = create_window(self)

    def start_capture(self):
        """Start the capture process when triggered from GUI"""
        # Hide GUI during capture
        self.window.withdraw()

        # Initialize selection window
        self.selection_window = SelectionWindow(
            dimensions=self.dimensions,
            on_selection_complete=self._on_selection_complete,
        )

        # Start selection window
        self.selection_window.start()

        # Show GUI after capture
        self.window.deiconify()

    def _on_selection_complete(self, bbox):
        """Simple wrapper to call controller and quit selection window."""
        try:
            # Get the text from controller
            text = self.controller.handle_selection(bbox)
            # Update the GUI with the text
            self.window.update_latest_capture(text)
        finally:
            self.selection_window.quit()
            # Show GUI again after capture
            self.window.deiconify()

    def run(self):
        """Start the application with GUI."""
        self.window.mainloop()


def main():
    app = ScreenCaptureOCR()
    app.run()


if __name__ == "__main__":
    main()
