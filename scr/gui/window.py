# gui/window.py
import customtkinter as ctk
import pyperclip


class OCRWindow(ctk.CTk):
    def __init__(self, app_controller):
        super().__init__()

        # Store controller reference
        self.app_controller = app_controller

        # Store latest capture
        self.latest_capture = ""

        # Configure window
        self.title("Medical Record OCR")
        self.geometry("800x600")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Make the capture text area expandable

        self.create_header()
        self.create_main_buttons()
        self.create_latest_capture_frame()

        # Add keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.on_capture_click())
        self.bind("<Control-c>", lambda e: self.on_copy_click())

    def create_header(self):
        """Create the header frame with title and description"""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="Medical Record OCR",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        description = ctk.CTkLabel(
            header_frame,
            text="Capture and format medical record text",
            font=ctk.CTkFont(size=14),
        )
        description.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

    def create_main_buttons(self):
        """Create the main action buttons"""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Create main action buttons
        buttons = [
            ("Capture (Ctrl+N)", self.on_capture_click),
            ("Copy Last (Ctrl+C)", self.on_copy_click),
            ("History", self.on_history_click),
            ("Settings", self.on_settings_click),
        ]

        for idx, (text, command) in enumerate(buttons):
            btn = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                width=120,
                height=80,
                font=ctk.CTkFont(size=16),
            )
            btn.grid(row=0, column=idx, padx=10, pady=10)

    def create_latest_capture_frame(self):
        """Create the frame showing the latest captured text"""
        capture_frame = ctk.CTkFrame(self)
        capture_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        capture_frame.grid_columnconfigure(0, weight=1)
        capture_frame.grid_rowconfigure(1, weight=1)

        # Label for the section
        label = ctk.CTkLabel(
            capture_frame,
            text="Latest Capture",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        # Text area for captured text
        self.capture_text = ctk.CTkTextbox(
            capture_frame, font=ctk.CTkFont(family="Courier", size=12), wrap="word"
        )
        self.capture_text.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.capture_text.insert("1.0", "No text captured yet")
        self.capture_text.configure(state="disabled")

    def on_capture_click(self):
        """Handle capture button click"""
        self.app_controller.start_capture()

    def on_copy_click(self):
        """Handle copy button click"""
        if self.latest_capture:
            pyperclip.copy(self.latest_capture)
            self.show_notification("Text copied to clipboard!")

    def on_history_click(self):
        """Handle history button click"""
        # TODO: Implement history window
        self.show_notification("History feature coming soon!")

    def on_settings_click(self):
        """Handle settings button click"""
        # TODO: Implement settings window
        self.show_notification("Settings feature coming soon!")

    def update_latest_capture(self, text):
        """Update the latest capture text"""
        self.latest_capture = text
        self.capture_text.configure(state="normal")
        self.capture_text.delete("1.0", "end")
        self.capture_text.insert("1.0", text)
        self.capture_text.configure(state="disabled")

    def show_notification(self, message):
        """Show a notification message"""
        notification = NotificationWindow(self, message)
        self.after(2000, notification.destroy)  # Destroy after 2 seconds


class NotificationWindow(ctk.CTkToplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.geometry("300x60")
        self.title("")

        # Remove window decorations
        self.overrideredirect(True)

        # Position window in bottom right corner
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = screen_width - 320
        y = screen_height - 100
        self.geometry(f"+{x}+{y}")

        # Add message
        label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14))
        label.pack(expand=True, fill="both", padx=20, pady=20)


def create_window(app_controller):
    return OCRWindow(app_controller)
