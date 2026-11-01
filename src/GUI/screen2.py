
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk, ImageEnhance


class Screen2Frame(ttk.Frame):

    def __init__(self, parent, controller=None, image_path=None, image=None):
        super().__init__(parent)

        self.controller = controller

        # -----------------------------------------------------
        # IMAGE DATA
        # -----------------------------------------------------

        if image is not None:
            self.original_image = image.copy()
        elif image_path:
            self.original_image = Image.open(image_path).copy()
        else:
            self.original_image = None

        self.cropped_image = (
            self.original_image.copy()
            if self.original_image is not None
            else None
        )

        self.current_display_image = None
        self.tk_preview = None

        # -----------------------------------------------------
        # CONTRAST STATE
        # -----------------------------------------------------

        self.contrast_factor = 1.0

        # -----------------------------------------------------
        # CROP SELECTION STATE
        # -----------------------------------------------------

        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None

        self.rect_id = None

        # Displayed image dimensions and offsets
        self.disp_width = 0
        self.disp_height = 0

        self.img_x_offset = 0
        self.img_y_offset = 0

        # -----------------------------------------------------
        # SETUP
        # -----------------------------------------------------

        self.setup_ui()

        if self.cropped_image is not None:
            self.after(100, self.update_preview)

    # ---------------------------------------------------------
    # UI SETUP
    # ---------------------------------------------------------

    def setup_ui(self):

        container = ttk.Frame(self, padding=20)
        container.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # HEADER
        # -----------------------------------------------------

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 15))

        title = ttk.Label(
            header,
            text="☆*VectorTrace*☆",
            style="Title.TLabel"
        )
        title.pack(anchor="center")

        subtitle = ttk.Label(
            header,
            text="Step 2: Crop & Adjust Contrast",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="center", pady=(4, 0))

        # -----------------------------------------------------
        # IMAGE PREVIEW AREA
        # -----------------------------------------------------

        preview_section = ttk.LabelFrame(
            container,
            text="  YOUR IMAGE  ",
            padding=15
        )
        preview_section.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        self.canvas_frame = tk.Frame(
            preview_section,
            bg="#eeeeee",
            relief="solid",
            borderwidth=1
        )
        self.canvas_frame.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="#eeeeee",
            highlightthickness=0
        )
        self.canvas.pack(
            fill="both",
            expand=True
        )

        # Crop selection mouse events
        self.canvas.bind(
            "<ButtonPress-1>",
            self.on_crop_press
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.on_crop_drag
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.on_crop_release
        )

        # -----------------------------------------------------
        # ADJUSTMENTS SECTION
        # -----------------------------------------------------

        controls_frame = ttk.LabelFrame(
            container,
            text="  ADJUSTMENTS  ",
            padding=15
        )
        controls_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        # -----------------------------------------------------
        # LEFT SIDE: CROP CONTROLS
        # -----------------------------------------------------

        crop_box = ttk.Frame(controls_frame)
        crop_box.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10
        )

        crop_label = ttk.Label(
            crop_box,
            text="CROP",
            style="Section.TLabel"
        )
        crop_label.pack(
            anchor="w",
            pady=(0, 4)
        )

        crop_desc = ttk.Label(
            crop_box,
            text="Drag on image, then click Crop.",
            style="Normal.TLabel"
        )
        crop_desc.pack(
            anchor="w",
            pady=(0, 8)
        )

        crop_btn_frame = ttk.Frame(crop_box)
        crop_btn_frame.pack(anchor="w")

        self.crop_btn = ttk.Button(
            crop_btn_frame,
            text="Crop Image",
            style="Action.TButton",
            width=14,
            command=self.apply_crop
        )
        self.crop_btn.pack(
            side="left",
            padx=(0, 8)
        )

        self.reset_crop_btn = ttk.Button(
            crop_btn_frame,
            text="Reset Crop",
            style="Action.TButton",
            width=14,
            command=self.reset_crop
        )
        self.reset_crop_btn.pack(side="left")

        # -----------------------------------------------------
        # RIGHT SIDE: CONTRAST CONTROLS
        # -----------------------------------------------------

        contrast_box = ttk.Frame(controls_frame)
        contrast_box.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=10
        )

        contrast_label = ttk.Label(
            contrast_box,
            text="CONTRAST",
            style="Section.TLabel"
        )
        contrast_label.pack(
            anchor="w",
            pady=(0, 4)
        )

        slider_container = ttk.Frame(contrast_box)
        slider_container.pack(
            fill="x",
            pady=5
        )

        low_lbl = ttk.Label(
            slider_container,
            text="Low",
            style="Normal.TLabel"
        )
        low_lbl.pack(side="left")

        self.contrast_slider = ttk.Scale(
            slider_container,
            from_=0.2,
            to=3.0,
            value=1.0,
            orient="horizontal",
            command=self.on_contrast_change
        )
        self.contrast_slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        high_lbl = ttk.Label(
            slider_container,
            text="High",
            style="Normal.TLabel"
        )
        high_lbl.pack(side="right")

        self.contrast_val_lbl = ttk.Label(
            contrast_box,
            text="Contrast: 1.0x",
            style="Normal.TLabel"
        )
        self.contrast_val_lbl.pack(
            anchor="w",
            pady=(2, 0)
        )

        # -----------------------------------------------------
        # NAVIGATION BUTTONS
        # -----------------------------------------------------

        nav_frame = ttk.Frame(container)
        nav_frame.pack(fill="x")

        self.back_button = ttk.Button(
            nav_frame,
            text="← Back",
            style="Action.TButton",
            width=12,
            command=self.go_back
        )
        self.back_button.pack(side="left")

        self.continue_button = ttk.Button(
            nav_frame,
            text="CONTINUE →",
            style="Upload.TButton",
            width=16,
            command=self.go_continue
        )
        self.continue_button.pack(side="right")

    # ---------------------------------------------------------
    # IMAGE PREVIEW AND RENDERING
    # ---------------------------------------------------------

    def update_preview(self, *args):

        if self.cropped_image is None:
            return

        # Apply contrast to the current cropped image
        enhancer = ImageEnhance.Contrast(self.cropped_image)

        enhanced_img = enhancer.enhance(
            self.contrast_factor
        )

        self.current_display_image = enhanced_img

        self.canvas.update_idletasks()

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 10 or ch <= 10:
            cw, ch = 700, 380

        # Fit image inside canvas while preserving aspect ratio
        img_copy = enhanced_img.copy()

        img_copy.thumbnail(
            (max(1, cw - 20), max(1, ch - 20)),
            Image.Resampling.LANCZOS
        )

        self.disp_width, self.disp_height = img_copy.size

        self.tk_preview = ImageTk.PhotoImage(img_copy)

        self.canvas.delete("all")

        self.img_x_offset = (
            cw - self.disp_width
        ) // 2

        self.img_y_offset = (
            ch - self.disp_height
        ) // 2

        self.canvas.create_image(
            self.img_x_offset,
            self.img_y_offset,
            anchor="nw",
            image=self.tk_preview
        )

        # Redraw crop rectangle if one exists
        if (
            self.crop_start_x is not None
            and self.crop_start_y is not None
            and self.crop_end_x is not None
            and self.crop_end_y is not None
        ):

            self.rect_id = self.canvas.create_rectangle(
                self.crop_start_x,
                self.crop_start_y,
                self.crop_end_x,
                self.crop_end_y,
                outline="#007acc",
                width=2,
                dash=(4, 4)
            )

    # ---------------------------------------------------------
    # CROP SELECTION HANDLERS
    # ---------------------------------------------------------

    def on_crop_press(self, event):

        if self.cropped_image is None:
            return

        if self.disp_width <= 0 or self.disp_height <= 0:
            return

        # Only start selection inside the displayed image
        if not (
            self.img_x_offset <= event.x <= self.img_x_offset + self.disp_width
            and
            self.img_y_offset <= event.y <= self.img_y_offset + self.disp_height
        ):
            return

        self.crop_start_x = event.x
        self.crop_start_y = event.y

        self.crop_end_x = event.x
        self.crop_end_y = event.y

        if self.rect_id is not None:
            self.canvas.delete(self.rect_id)

        self.rect_id = self.canvas.create_rectangle(
            self.crop_start_x,
            self.crop_start_y,
            self.crop_end_x,
            self.crop_end_y,
            outline="#007acc",
            width=2,
            dash=(4, 4)
        )

    def on_crop_drag(self, event):

        if self.crop_start_x is None:
            return

        # Keep selection inside the displayed image
        self.crop_end_x = max(
            self.img_x_offset,
            min(event.x, self.img_x_offset + self.disp_width)
        )

        self.crop_end_y = max(
            self.img_y_offset,
            min(event.y, self.img_y_offset + self.disp_height)
        )

        if self.rect_id is not None:
            self.canvas.coords(
                self.rect_id,
                self.crop_start_x,
                self.crop_start_y,
                self.crop_end_x,
                self.crop_end_y
            )

    def on_crop_release(self, event):

        if self.crop_start_x is None:
            return

        self.on_crop_drag(event)

    # ---------------------------------------------------------
    # APPLY CROP
    # ---------------------------------------------------------

    def apply_crop(self):

        if self.cropped_image is None:
            messagebox.showwarning(
                "Crop Error",
                "No image is available to crop."
            )
            return

        if None in (
            self.crop_start_x,
            self.crop_start_y,
            self.crop_end_x,
            self.crop_end_y
        ):
            messagebox.showwarning(
                "Crop Error",
                "Please drag a box over the image first."
            )
            return

        # Convert canvas coordinates into image coordinates
        x1 = min(
            self.crop_start_x,
            self.crop_end_x
        ) - self.img_x_offset

        y1 = min(
            self.crop_start_y,
            self.crop_end_y
        ) - self.img_y_offset

        x2 = max(
            self.crop_start_x,
            self.crop_end_x
        ) - self.img_x_offset

        y2 = max(
            self.crop_start_y,
            self.crop_end_y
        ) - self.img_y_offset

        # Restrict selection to displayed image boundaries
        x1 = max(0, min(x1, self.disp_width))
        y1 = max(0, min(y1, self.disp_height))

        x2 = max(0, min(x2, self.disp_width))
        y2 = max(0, min(y2, self.disp_height))

        if x2 - x1 < 10 or y2 - y1 < 10:
            messagebox.showwarning(
                "Invalid Selection",
                "Selection area is too small."
            )
            return

        # Convert displayed coordinates to original image coordinates
        orig_w, orig_h = self.cropped_image.size

        scale_x = orig_w / self.disp_width
        scale_y = orig_h / self.disp_height

        crop_box = (
            int(x1 * scale_x),
            int(y1 * scale_y),
            int(x2 * scale_x),
            int(y2 * scale_y)
        )

        # Apply crop
        self.cropped_image = self.cropped_image.crop(
            crop_box
        )

        # Clear selection
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None

        self.rect_id = None

        # Refresh preview
        self.update_preview()

    # ---------------------------------------------------------
    # RESET CROP
    # ---------------------------------------------------------

    
    def reset_crop(self):

        if self.original_image is None:
            return

        # Restore the original image without changing contrast
        self.cropped_image = self.original_image.copy()

        # Clear crop selection
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.rect_id = None

        # Keep the existing contrast factor
        # The preview will automatically apply it again
        self.update_preview()

    # ---------------------------------------------------------
    # CONTRAST SLIDER HANDLER
    # ---------------------------------------------------------

    def on_contrast_change(self, val):

        self.contrast_factor = float(val)

        self.contrast_val_lbl.config(
            text=f"Contrast: {self.contrast_factor:.1f}x"
        )

        self.update_preview()

    # ---------------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------------

    def go_back(self):

        if self.controller and hasattr(
            self.controller,
            "show_screen1"
        ):
            self.controller.show_screen1()

    def go_continue(self):

        if self.current_display_image is None:
            messagebox.showwarning(
                "No Image",
                "Please upload an image before continuing."
            )
            return

        if self.controller and hasattr(
            self.controller,
            "show_screen3"
        ):
            self.controller.show_screen3(
                self.current_display_image.copy()
            )

        else:
            messagebox.showinfo(
                "Continue",
                "Transitioning to Screen 3 (Processing)..."
            )


# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    root.title("Vector Trace — Screen 2")
    root.geometry("1000x700")

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 24, "bold")
    )

    style.configure(
        "Subtitle.TLabel",
        font=("Segoe UI", 11)
    )

    style.configure(
        "Section.TLabel",
        font=("Segoe UI", 12, "bold")
    )

    style.configure(
        "Normal.TLabel",
        font=("Segoe UI", 10)
    )

    style.configure(
        "Upload.TButton",
        font=("Segoe UI", 11, "bold"),
        padding=(10, 6)
    )

    style.configure(
        "Action.TButton",
        font=("Segoe UI", 10),
        padding=(8, 4)
    )

    dummy_img = Image.new(
        "RGB",
        (600, 400),
        color=(220, 220, 220)
    )

    screen2 = Screen2Frame(
        root,
        controller=None,
        image=dummy_img
    )

    screen2.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
