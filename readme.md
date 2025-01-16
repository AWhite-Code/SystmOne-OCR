Program to OCR the notes summary section

# Development Setup

## Setting up Tesseract

This project requires Tesseract OCR version 5.3.1. To set up the development environment:

1. Run the setup script:
   ```bash
   python setup.py
   ```

2. Follow the prompts to:
   - Download Tesseract
   - Install it on your system
   - Copy necessary files to the project's vendor directory

The setup script will handle downloading and configuring Tesseract in your project directory.

## Manually Setting Up Tesseract

If you prefer to set up Tesseract manually:

1. Download Tesseract 5.3.1 from [UB-Mannheim's GitHub](https://github.com/UB-Mannheim/tesseract/releases/tag/v5.3.1)
2. Install Tesseract
3. Create a `vendor/tesseract` directory in the project root
4. Copy these files from your Tesseract installation:
   - `tesseract.exe`
   - The entire `tessdata` folder
   
The project will look for Tesseract in `vendor/tesseract/tesseract.exe`