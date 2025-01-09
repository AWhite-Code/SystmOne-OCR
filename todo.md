Refactor into multiple files:
├── systmone_ocr.py       # Main script
├── ui.py                 # Mouse Events, Window Management
├── image_processing.py   # Preprocess Image, Capture_screen
├── ocr_processing.py     # process_text, format_date, clean_description
└── clipboard_utils.py    # Saving to clipboard

regex(?) to delete read codes

Removal of Admin codes (Notes Summary, Computer Summary)

Add GUI interface

Add "Always on" with hotkey to activate.

Add Cancel button during 'screenshot' process