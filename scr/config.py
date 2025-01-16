from pathlib import Path

# Project base paths
PROJECT_ROOT = Path(__file__).parent.parent
VENDOR_DIR = PROJECT_ROOT / 'vendor'

# Tesseract configuration
TESSERACT_PATH = str(VENDOR_DIR / 'tesseract' / 'tesseract.exe')

# GUI configuration
OVERLAY_ALPHA = 0.3  # Transparency level for the overlay window
SELECTION_BORDER_COLOR = '#FF0000'  # Red border for selection
SELECTION_BORDER_WIDTH = 6

# Image processing configuration
IMAGE_SCALE_FACTOR = 3
CONTRAST_ENHANCE_FACTOR = 3.0
BRIGHTNESS_ENHANCE_FACTOR = 1.1
IMAGE_PADDING = 20

# Debug configuration
DEBUG_MODE = False
SAVE_DEBUG_IMAGE = True
DEBUG_IMAGE_PATH = PROJECT_ROOT / 'debug_ocr.png'