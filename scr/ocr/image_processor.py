from PIL import Image, ImageOps, ImageEnhance
import pytesseract
from config import (
    IMAGE_SCALE_FACTOR,
    CONTRAST_ENHANCE_FACTOR,
    BRIGHTNESS_ENHANCE_FACTOR,
    IMAGE_PADDING,
    SAVE_DEBUG_IMAGE,
    DEBUG_IMAGE_PATH,
)


class ImageProcessor:
    def __init__(self, tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.ocr_config = r"--oem 3 --psm 6 -c preserve_interword_spaces=1"

    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy for blue text.
        """
        # Convert to RGB if not already
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Scale up first to avoid losing detail
        scaled = image.resize(
            (image.width * IMAGE_SCALE_FACTOR, image.height * IMAGE_SCALE_FACTOR),
            Image.Resampling.LANCZOS,
        )

        # Convert to grayscale
        gray = ImageOps.grayscale(scaled)

        # Increase contrast
        contrast = ImageEnhance.Contrast(gray).enhance(CONTRAST_ENHANCE_FACTOR)

        # Slightly increase brightness to make text clearer
        brightness = ImageEnhance.Brightness(contrast).enhance(
            BRIGHTNESS_ENHANCE_FACTOR
        )

        # Add padding around the image to help with character recognition
        padded = ImageOps.expand(brightness, border=IMAGE_PADDING, fill=255)

        # Save debug image if enabled
        if SAVE_DEBUG_IMAGE:
            padded.save(DEBUG_IMAGE_PATH)

        return padded

    def perform_ocr(self, image):
        """
        Perform OCR on the preprocessed image.
        """
        return pytesseract.image_to_string(image, config=self.ocr_config)
