# gui/window.py
import customtkinter as ctk


class OCRWindow(ctk.CTk):
    def __init__(self, app_controller):
        super().__init__()

        # Store controller reference
        self.app_controller = app_controller

        # Configure window
        self.title("Medical Record OCR")
        self.geometry("800x600")

        # Configure grid layout (2x1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create a simple label
        self.label = ctk.CTkLabel(
            self, text="Medical Record OCR", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label.grid(row=0, column=0, padx=20, pady=20)

        # Create a simple button
        self.button = ctk.CTkButton(self, text="Capture", command=self.on_capture_click)
        self.button.grid(row=1, column=0, padx=20, pady=20)

    def on_capture_click(self):
        """Handle capture button click"""
        self.app_controller.start_capture()


def create_window(app_controller):
    return OCRWindow(app_controller)
