import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


class VectorTraceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vector Trace — Doodle to Vector")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)

        self.image = None
        self.preview_image = None
        self.image_path = None

        self.setup_style()
        self.create_page()

    # ---------------------------------------------------------
    # STYLING
    # ---------------------------------------------------------

    def setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 26, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 12)
        )

        style.configure(
            "Section.TLabel",
            font=("Segoe UI", 14, "bold")
        )

        style.configure(
            "Normal.TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Upload.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(20, 10)
        )

        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10),
            padding=(15, 8)
        )

    # ---------------------------------------------------------
    # PAGE 1
    # ---------------------------------------------------------

    def create_page(self):

        # Main container
        main_frame = ttk.Frame(self.root, padding=30)
        main_frame.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = ttk.Frame(main_frame)
        header.pack(fill="x", pady=(0, 25))

        title = ttk.Label(
            header,
            text="VECTOR TRACE",
            style="Title.TLabel"
        )
        title.pack(anchor="center")

        subtitle = ttk.Label(
            header,
            text="Doodle → Clean Vector",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="center", pady=(4, 0))

        # -----------------------------------------------------
        # INPUT SECTION
        # -----------------------------------------------------

        input_section = ttk.LabelFrame(
            main_frame,
            text="  INPUT  ",
            padding=20
        )
        input_section.pack(fill="x", pady=(0, 20))

        # Upload button
        self.upload_button = ttk.Button(
            input_section,
            text="Upload Image",
            style="Upload.TButton",
            command=self.upload_image
        )
        self.upload_button.pack(pady=(5, 10))

        # Supported formats
        supported_label = ttk.Label(
            input_section,
            text="Supported: JPG • JPEG • PNG",
            style="Normal.TLabel"
        )
        supported_label.pack()

        # Selected file
        self.file_label = ttk.Label(
            input_section,
            text="No image selected",
            style="Normal.TLabel"
        )
        self.file_label.pack(pady=(12, 5))

        # -----------------------------------------------------
        # PREVIEW SECTION
        # -----------------------------------------------------

        preview_section = ttk.LabelFrame(
            main_frame,
            text="  PREVIEW  ",
            padding=15
        )
        preview_section.pack(
            fill="both",
            expand=True,
            pady=(0, 20)
        )

        # Preview title
        original_label = ttk.Label(
            preview_section,
            text="ORIGINAL",
            style="Section.TLabel"
        )
        original_label.pack(pady=(0, 10))

        # Image display area
        self.image_frame = tk.Frame(
            preview_section,
            bg="#eeeeee",
            relief="solid",
            borderwidth=1
        )
        self.image_frame.pack(
            fill="both",
            expand=True,
            padx=20
        )

        self.image_label = tk.Label(
            self.image_frame,
            text="Upload an image to preview it",
            font=("Segoe UI", 11),
            bg="#eeeeee",
            fg="#666666"
        )
        self.image_label.pack(
            fill="both",
            expand=True
        )

        # -----------------------------------------------------
        # ACTION BUTTONS
        # -----------------------------------------------------

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        self.crop_button = ttk.Button(
            button_frame,
            text="Crop Image",
            style="Action.TButton",
            command=self.crop_image,
            state="disabled"
        )
        self.crop_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.process_button = ttk.Button(
            button_frame,
            text="Process / Vectorize",
            style="Action.TButton",
            command=self.process_image,
            state="disabled"
        )
        self.process_button.pack(
            side="right"
        )

    # ---------------------------------------------------------
    # UPLOAD IMAGE
    # ---------------------------------------------------------

    def upload_image(self):

        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png"),
                ("JPG Files", "*.jpg"),
                ("JPEG Files", "*.jpeg"),
                ("PNG Files", "*.png")
            ]
        )

        if not file_path:
            return

        # Validate extension
        extension = os.path.splitext(file_path)[1].lower()

        if extension not in [".jpg", ".jpeg", ".png"]:
            messagebox.showerror(
                "Invalid File",
                "Please select a JPG, JPEG, or PNG image."
            )
            return

        try:
            # Open image using Pillow
            self.image = Image.open(file_path)
            self.image_path = file_path

            # Display filename
            filename = os.path.basename(file_path)

            self.file_label.config(
                text=f"Selected: {filename}"
            )

            # Display image
            self.display_image()

            # Enable buttons
            self.crop_button.config(state="normal")
            self.process_button.config(state="normal")

        except Exception:
            messagebox.showerror(
                "Error",
                "Unable to open this image.\n"
                "Please try another image."
            )

    # ---------------------------------------------------------
    # DISPLAY IMAGE
    # ---------------------------------------------------------

    def display_image(self):

        if self.image is None:
            return

        # Get available preview area
        self.image_frame.update_idletasks()

        max_width = self.image_frame.winfo_width() - 40
        max_height = self.image_frame.winfo_height() - 40

        # Prevent invalid dimensions during startup
        if max_width <= 0:
            max_width = 700

        if max_height <= 0:
            max_height = 400

        # Make a copy
        preview = self.image.copy()

        # Maintain aspect ratio
        preview.thumbnail(
            (max_width, max_height),
            Image.Resampling.LANCZOS
        )

        # Convert for Tkinter
        self.preview_image = ImageTk.PhotoImage(preview)

        self.image_label.config(
            image=self.preview_image,
            text=""
        )

    # ---------------------------------------------------------
    # CROP
    # ---------------------------------------------------------

    def crop_image(self):

        messagebox.showinfo(
            "Crop Image",
            "Crop functionality will be connected here."
        )

    # ---------------------------------------------------------
    # PROCESS
    # ---------------------------------------------------------

    def process_image(self):

        messagebox.showinfo(
            "Process / Vectorize",
            "Image processing will be connected here."
        )


# -------------------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = VectorTraceApp(root)

    root.mainloop()