import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageEnhance


class Screen2Frame(ttk.Frame):
    def __init__(self, parent, controller=None, image_path=None, image=None):
        super().__init__(parent)
        self.controller = controller

        # Working images (original base, working base, and displayed image)
        self.original_image = image if image else (Image.open(image_path) if image_path else None)
        self.cropped_image = self.original_image.copy() if self.original_image else None
        self.current_display_image = None
        self.tk_preview = None

        # Contrast adjustment state
        self.contrast_factor = 1.0

        # Crop selection rectangle coordinates (Canvas relative)
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.rect_id = None

        self.setup_ui()
        if self.cropped_image:
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
        # PREVIEW AREA (CANVAS)
        # -----------------------------------------------------
        preview_section = ttk.LabelFrame(
            container,
            text="  YOUR IMAGE  ",
            padding=15
        )
        preview_section.pack(fill="both", expand=True, pady=(0, 15))

        self.canvas_frame = tk.Frame(
            preview_section,
            bg="#eeeeee",
            relief="solid",
            borderwidth=1
        )
        self.canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="#eeeeee",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Canvas mouse bindings for crop box selection
        self.canvas.bind("<ButtonPress-1>", self.on_crop_press)
        self.canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_crop_release)

        # -----------------------------------------------------
        # CONTROL CONTRAST & CROP SECTION
        # -----------------------------------------------------
        controls_frame = ttk.LabelFrame(
            container,
            text="  ADJUSTMENTS  ",
            padding=15
        )
        controls_frame.pack(fill="x", pady=(0, 15))

        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)

        # --- LEFT: CROP TOOL ---
        crop_box = ttk.Frame(controls_frame)
        crop_box.grid(row=0, column=0, sticky="nsew", padx=10)

        crop_label = ttk.Label(
            crop_box,
            text="CROP",
            style="Section.TLabel"
        )
        crop_label.pack(anchor="w", pady=(0, 4))

        crop_desc = ttk.Label(
            crop_box,
            text="Drag on image, then click Crop.",
            style="Normal.TLabel"
        )
        crop_desc.pack(anchor="w", pady=(0, 8))

        crop_btn_frame = ttk.Frame(crop_box)
        crop_btn_frame.pack(anchor="w")

        self.crop_btn = ttk.Button(
            crop_btn_frame,
            text="Crop Image",
            style="Action.TButton",
            width=14,
            command=self.apply_crop
        )
        self.crop_btn.pack(side="left", padx=(0, 8))

        self.reset_crop_btn = ttk.Button(
            crop_btn_frame,
            text="Reset Crop",
            style="Action.TButton",
            width=14,
            command=self.reset_crop
        )
        self.reset_crop_btn.pack(side="left")

        # --- RIGHT: CONTRAST SLIDER ---
        contrast_box = ttk.Frame(controls_frame)
        contrast_box.grid(row=0, column=1, sticky="nsew", padx=10)

        contrast_label = ttk.Label(
            contrast_box,
            text="CONTRAST",
            style="Section.TLabel"
        )
        contrast_label.pack(anchor="w", pady=(0, 4))

        slider_container = ttk.Frame(contrast_box)
        slider_container.pack(fill="x", pady=5)

        low_lbl = ttk.Label(slider_container, text="Low", style="Normal.TLabel")
        low_lbl.pack(side="left")

        self.contrast_slider = ttk.Scale(
            slider_container,
            from_=0.2,
            to=3.0,
            value=1.0,
            orient="horizontal",
            command=self.on_contrast_change
        )
        self.contrast_slider.pack(side="left", fill="x", expand=True, padx=8)

        high_lbl = ttk.Label(slider_container, text="High", style="Normal.TLabel")
        high_lbl.pack(side="right")

        self.contrast_val_lbl = ttk.Label(
            contrast_box,
            text="Contrast: 1.0x",
            style="Normal.TLabel"
        )
        self.contrast_val_lbl.pack(anchor="w", pady=(2, 0))

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
    # IMAGE PREVIEW & RENDERING
    # ---------------------------------------------------------
    def update_preview(self, *args):
        if self.cropped_image is None:
            return

        enhancer = ImageEnhance.Contrast(self.cropped_image)
        enhanced_img = enhancer.enhance(self.contrast_factor)
        self.current_display_image = enhanced_img

        self.canvas.update_idletasks()
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 10 or ch <= 10:
            cw, ch = 700, 380

        img_copy = enhanced_img.copy()
        img_copy.thumbnail((cw - 20, ch - 20), Image.Resampling.LANCZOS)

        self.disp_width, self.disp_height = img_copy.size
        self.tk_preview = ImageTk.PhotoImage(img_copy)

        self.canvas.delete("all")
        self.img_x_offset = (cw - self.disp_width) // 2
        self.img_y_offset = (ch - self.disp_height) // 2

        self.canvas.create_image(
            self.img_x_offset,
            self.img_y_offset,
            anchor="nw",
            image=self.tk_preview
        )

        if self.crop_start_x is not None and self.crop_end_x is not None:
            self.rect_id = self.canvas.create_rectangle(
                self.crop_start_x, self.crop_start_y,
                self.crop_end_x, self.crop_end_y,
                outline="#007acc", width=2, dash=(4, 4)
            )

    # ---------------------------------------------------------
    # CROP SELECTION HANDLERS
    # ---------------------------------------------------------
    def on_crop_press(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            self.crop_start_x, self.crop_start_y,
            outline="#007acc", width=2, dash=(4, 4)
        )

    def on_crop_drag(self, event):
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        if self.rect_id:
            self.canvas.coords(
                self.rect_id,
                self.crop_start_x, self.crop_start_y,
                self.crop_end_x, self.crop_end_y
            )

    def on_crop_release(self, event):
        self.crop_end_x = event.x
        self.crop_end_y = event.y

    def apply_crop(self):
        if None in (self.crop_start_x, self.crop_start_y, self.crop_end_x, self.crop_end_y):
            messagebox.showwarning("Crop Error", "Please drag a box over the image first.")
            return

        x1 = min(self.crop_start_x, self.crop_end_x) - self.img_x_offset
        y1 = min(self.crop_start_y, self.crop_end_y) - self.img_y_offset
        x2 = max(self.crop_start_x, self.crop_end_x) - self.img_x_offset
        y2 = max(self.crop_start_y, self.crop_end_y) - self.img_y_offset

        orig_w, orig_h = self.cropped_image.size
        scale_x = orig_w / self.disp_width
        scale_y = orig_h / self.disp_height

        crop_box = (
            max(0, int(x1 * scale_x)),
            max(0, int(y1 * scale_y)),
            min(orig_w, int(x2 * scale_x)),
            min(orig_h, int(y2 * scale_y))
        )

        if crop_box[2] - crop_box[0] > 10 and crop_box[3] - crop_box[1] > 10:
            self.cropped_image = self.cropped_image.crop(crop_box)
            self.crop_start_x = self.crop_start_y = self.crop_end_x = self.crop_end_y = None
            self.update_preview()
        else:
            messagebox.showwarning("Invalid Selection", "Selection area is too small.")

    def reset_crop(self):
        if self.original_image:
            self.cropped_image = self.original_image.copy()
            self.crop_start_x = self.crop_start_y = self.crop_end_x = self.crop_end_y = None
            self.contrast_slider.set(1.0)
            self.contrast_factor = 1.0
            self.contrast_val_lbl.config(text="Contrast: 1.0x")
            self.update_preview()

    # ---------------------------------------------------------
    # CONTRAST SLIDER HANDLER
    # ---------------------------------------------------------
    def on_contrast_change(self, val):
        self.contrast_factor = float(val)
        self.contrast_val_lbl.config(text=f"Contrast: {self.contrast_factor:.1f}x")
        self.update_preview()

    # ---------------------------------------------------------
    # NAVIGATION
    # ---------------------------------------------------------
    def go_back(self):
        if self.controller and hasattr(self.controller, "show_screen1"):
            self.controller.show_screen1()

    def go_continue(self):
        if self.controller and hasattr(self.controller, "show_screen3"):
            self.controller.show_screen3(self.current_display_image)
        else:
            messagebox.showinfo("Continue", "Transitioning to Screen 3 (Processing)...")


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
    except:
        pass

    style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
    style.configure("Subtitle.TLabel", font=("Segoe UI", 11))
    style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Normal.TLabel", font=("Segoe UI", 10))
    style.configure("Upload.TButton", font=("Segoe UI", 11, "bold"), padding=(10, 6))
    style.configure("Action.TButton", font=("Segoe UI", 10), padding=(8, 4))

    dummy_img = Image.new("RGB", (600, 400), color=(220, 220, 220))
    screen2 = Screen2Frame(root, controller=None, image=dummy_img)
    screen2.pack(fill="both", expand=True)

    root.mainloop()