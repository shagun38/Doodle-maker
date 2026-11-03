
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue

from Integration.pipeline import process_pil_image


class Screen3Frame(ttk.Frame):
    def __init__(self, parent, controller=None, image=None, result=None):
        super().__init__(parent)

        self.controller = controller
        self.image = image

        # Previously processed result, if available
        self.result = result

        self.progress_val = 0
        self.progress_queue = queue.Queue()
        self.processing_started = False

        self.setup_ui()

        # Start processing after the UI is displayed
        self.after(300, self.start_processing)
        

    def go_back(self):
        print("========== SCREEN 3 BACK CLICKED ==========")

        if self.controller:
            print("Controller exists")
            print("Opening Screen 2")

            self.controller.show_screen2(
                image=self.image
            )
        else:
            print("Controller is missing")

    # ---------------------------------------------------------
    # UI SETUP
    # ---------------------------------------------------------
    def setup_ui(self):
        # Outer container centered in the window
        container = ttk.Frame(self, padding=40)
        container.pack(expand=True)

        # 1. Header Brand
        brand_label = ttk.Label(
            container,
            text="☆*VectorTrace*☆",
            font=("Segoe UI", 20, "bold"),
            foreground="#333333"
        )
        brand_label.pack(anchor="center", pady=(0, 40))

        # 2. Status Titles
        title_label = ttk.Label(
            container,
            text="Processing Image",
            font=("Segoe UI", 16, "bold"),
            foreground="#111111"
        )
        title_label.pack(anchor="center", pady=(0, 8))

        subtitle_label = ttk.Label(
            container,
            text="Converting your masterpiece into\nvector artwork!!\n\n(*°▽°*)",
            font=("Segoe UI", 11),
            foreground="#666666",
            justify="center"
        )
        subtitle_label.pack(anchor="center", pady=(0, 35))

        # 3. Custom Visual Progress Bar (Canvas)
        self.bar_width = 320
        self.bar_height = 18

        self.progress_canvas = tk.Canvas(
            container,
            width=self.bar_width,
            height=self.bar_height,
            bg="#e0e0e0",
            highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.progress_canvas.pack(anchor="center", pady=(0, 12))

        # Draw inner progress rectangle (initially 0 width)
        self.progress_rect = self.progress_canvas.create_rectangle(
            0, 0, 0, self.bar_height,
            fill="#3bc8fc",
            width=0
        )

        # 4. Percentage Readout
        self.percent_label = ttk.Label(
            container,
            text="0%",
            font=("Segoe UI", 14, "bold"),
            foreground="#222222"
        )
        self.percent_label.pack(anchor="center", pady=(0, 25))

        # 5. Footer Status
        self.wait_label = ttk.Label(
            container,
            text="Please wait...",
            font=("Segoe UI", 10, "italic"),
            foreground="#888888"
        )
        self.wait_label.pack(anchor="center")

        # Back button
        self.back_button = ttk.Button(
            container,
            text="← Back",
            command=self.go_back
        )
        self.back_button.pack(anchor="center", pady=(25, 0))

    # ---------------------------------------------------------
    # PROGRESS BAR LOGIC
    # ---------------------------------------------------------
    def update_progress_bar(self, percentage):
        """Update the progress bar and percentage text."""

        self.progress_val = min(100, max(0, percentage))

        fill_width = (
            self.progress_val / 100.0
        ) * self.bar_width

        self.progress_canvas.coords(
            self.progress_rect,
            0, 0, fill_width, self.bar_height
        )

        self.percent_label.config(
            text=f"{int(self.progress_val)}%"
        )

    # ---------------------------------------------------------
    # PROCESSING LOGIC
    # ---------------------------------------------------------
    def start_processing(self):
        """Start actual image processing in a background thread."""

        if not self.winfo_exists():
            return

        # Reuse the result if the image was already processed.
        # Reuse the result if the image was already processed.
        if self.result is not None:
            self.update_progress_bar(100)
            self.wait_label.config(text="Processing completed!")
            return

        if self.processing_started:
            return

        if self.image is None:
            self.handle_processing_error(
                "No image was received from Screen 2."
            )
            return

        self.processing_started = True
        self.wait_label.config(text="Starting image processing...")

        # Start the worker thread
        worker_thread = threading.Thread(
            target=self.processing_worker,
            daemon=True
        )
        worker_thread.start()

        # Check for progress updates from the worker
        self.check_processing_queue()

    def processing_worker(self):
        """
        Run the pipeline in a background thread.

        The worker communicates with Tkinter through a queue.
        It never directly updates GUI widgets.
        """

        try:
            result = process_pil_image(
                self.image,
                progress_callback=self.report_progress
            )

            self.progress_queue.put(("success", result))

        except Exception as exc:
            self.progress_queue.put(("error", str(exc)))

    def report_progress(self, stage, percentage):
        """Send pipeline progress information to the GUI thread."""

        self.progress_queue.put(
            ("progress", stage, percentage)
        )

    # ---------------------------------------------------------
    # THREAD-SAFE GUI UPDATES
    # ---------------------------------------------------------
    def check_processing_queue(self):
        """Read worker messages and safely update the GUI."""

        if not self.winfo_exists():
            return

        try:
            while True:
                message = self.progress_queue.get_nowait()
                message_type = message[0]

                if message_type == "progress":
                    stage = message[1]
                    percentage = message[2]

                    self.update_progress_bar(percentage)
                    self.wait_label.config(text=stage)

                elif message_type == "success":
                    self.result = message[1]

                    # Store the result in the main application
                    if self.controller:
                        self.controller.processing_result = self.result

                    self.update_progress_bar(100)
                    self.wait_label.config(
                        text="Processing completed!"
                    )

                    self.after(400, self.finish_processing)
                    return

                elif message_type == "error":
                    error_message = message[1]
                    self.handle_processing_error(error_message)
                    return

        except queue.Empty:
            pass

        # Continue checking for worker updates
        self.after(100, self.check_processing_queue)

    # ---------------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------------
    def handle_processing_error(self, error_message):
        """Display processing errors on the main GUI thread."""

        self.wait_label.config(text="Processing failed.")

        messagebox.showerror(
            "Processing Error",
            f"Could not process the image:\n\n{error_message}",
            parent=self
        )

    # ---------------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------------
    def finish_processing(self):
        """Pass the processed result to Screen 4."""

        if not self.winfo_exists():
            return

        if not self.controller or not hasattr(
            self.controller, "show_screen4"
        ):
            return

        # Use the application cache as a fallback
        result = self.result

        if result is None:
            result = self.controller.processing_result

        if result is None:
            self.handle_processing_error(
                "Processing finished, but no result was received."
            )
            return

        self.controller.show_screen4(
            image=self.image,
            result=result
        )
# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    from PIL import Image

    root = tk.Tk()
    root.title("Vector Trace — Screen 3")
    root.geometry("1000x700")

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Sample image for standalone testing
    test_image = Image.new(
        "RGB",
        (300, 300),
        "white"
    )

    screen3 = Screen3Frame(
        root,
        controller=None,
        image=test_image
    )

    screen3.pack(fill="both", expand=True)

    root.mainloop()
