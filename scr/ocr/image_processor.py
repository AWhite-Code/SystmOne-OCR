from PIL import Image, ImageOps, ImageEnhance
import pytesseract

class ImageProcessor:
    def __init__(self, tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        self.ocr_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'

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
        
        # Save debug image if needed
        padded.save('debug_ocr.png')
        
        return padded

    def perform_ocr(self, image):
        """
        Perform OCR on the preprocessed image.
        """
        return pytesseract.image_to_string(image, config=self.ocr_config)