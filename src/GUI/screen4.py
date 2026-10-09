import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter


class Screen4Frame(ttk.Frame):
    def __init__(self, parent, controller=None, image=None):
        super().__init__(parent)
        self.controller = controller

        # Working image from Screen 2
        self.original_image = image if image else self.create_dummy_image()
        self.vector_image = None
        
        # Display image references to prevent Tkinter garbage collection
        self.tk_orig_preview = None
        self.tk_vec_preview = None

        # User Options
        self.remove_bg_var = tk.BooleanVar(value=False)
        self.export_format_var = tk.StringVar(value="SVG")

        self.setup_ui()
        self.after(100, self.process_and_update)

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
            text="Results!! How do you like it?? (❁´◡`❁)",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="center", pady=(4, 0))

        # -----------------------------------------------------
        # PREVIEW AREA (SIDE BY SIDE COMPARISON)
        # -----------------------------------------------------
        preview_section = ttk.LabelFrame(
            container,
            text="  COMPARISON  ",
            padding=15
        )
        preview_section.pack(fill="both", expand=True, pady=(0, 15))

        preview_grid = ttk.Frame(preview_section)
        preview_grid.pack(fill="both", expand=True)

        preview_grid.columnconfigure(0, weight=1)
        preview_grid.columnconfigure(1, weight=0)
        preview_grid.columnconfigure(2, weight=1)
        preview_grid.rowconfigure(1, weight=1)

        # --- LEFT: ORIGINAL DOODLE ---
        orig_lbl = ttk.Label(preview_grid, text="ORIGINAL", style="Section.TLabel")
        orig_lbl.grid(row=0, column=0, pady=(0, 8))

        self.orig_frame = tk.Frame(preview_grid, bg="#eeeeee", relief="solid", borderwidth=1)
        self.orig_frame.grid(row=1, column=0, sticky="nsew", padx=5)

        self.orig_canvas = tk.Canvas(self.orig_frame, bg="#eeeeee", highlightthickness=0)
        self.orig_canvas.pack(fill="both", expand=True)

        # --- CENTER: ARROW ---
        arrow_lbl = ttk.Label(preview_grid, text="➔", font=("Segoe UI", 24, "bold"), foreground="#666666")
        arrow_lbl.grid(row=1, column=1, padx=15)

        # --- RIGHT: VECTOR RESULT ---
        vec_lbl = ttk.Label(preview_grid, text="VECTOR RESULT", style="Section.TLabel")
        vec_lbl.grid(row=0, column=2, pady=(0, 8))

        self.vec_frame = tk.Frame(preview_grid, bg="#ffffff", relief="solid", borderwidth=1)
        self.vec_frame.grid(row=1, column=2, sticky="nsew", padx=5)

        self.vec_canvas = tk.Canvas(self.vec_frame, bg="#ffffff", highlightthickness=0)
        self.vec_canvas.pack(fill="both", expand=True)

        # -----------------------------------------------------
        # OPTIONS SECTION
        # -----------------------------------------------------
        options_frame = ttk.LabelFrame(
            container,
            text="  EXPORT OPTIONS  ",
            padding=15
        )
        options_frame.pack(fill="x", pady=(0, 15))

        # Checkbox: Remove Background
        self.bg_checkbox = ttk.Checkbutton(
            options_frame,
            text="Remove Background (Transparent)",
            variable=self.remove_bg_var,
            command=self.process_and_update
        )
        self.bg_checkbox.pack(anchor="w", pady=(0, 10))

        # Radio Buttons: Format
        fmt_frame = ttk.Frame(options_frame)
        fmt_frame.pack(anchor="w")

        fmt_label = ttk.Label(fmt_frame, text="Download as: ", style="Normal.TLabel")
        fmt_label.pack(side="left", padx=(0, 10))

        svg_radio = ttk.Radiobutton(
            fmt_frame,
            text="SVG (Vector)",
            value="SVG",
            variable=self.export_format_var
        )
        svg_radio.pack(side="left", padx=(0, 15))

        png_radio = ttk.Radiobutton(
            fmt_frame,
            text="PNG (Raster)",
            value="PNG",
            variable=self.export_format_var
        )
        png_radio.pack(side="left")

        # -----------------------------------------------------
        # NAVIGATION / ACTION BUTTONS
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

        self.download_button = ttk.Button(
            nav_frame,
            text="↓ DOWNLOAD",
            style="Upload.TButton",
            width=16,
            command=self.download_file
        )
        self.download_button.pack(side="right")

    # ---------------------------------------------------------
    # VECTOR PROCESSING & PREVIEW UPDATE
    # ---------------------------------------------------------
    def process_and_update(self, *args):
        if self.original_image is None:
            return

        # 1. Convert image to clean black & white line art (Vector style)
        gray_img = self.original_image.convert("L")
        
        # Apply thresholding to create sharp doodle edges
        threshold = 180
        bw_img = gray_img.point(lambda p: 255 if p > threshold else 0)

        if self.remove_bg_var.get():
            # Create RGBA image with transparent background for white pixels
            rgba_img = Image.new("RGBA", bw_img.size, (255, 255, 255, 0))
            pixels = bw_img.load()
            rgba_pixels = rgba_img.load()

            for y in range(bw_img.height):
                for x in range(bw_img.width):
                    if pixels[x, y] == 0:  # Black lines
                        rgba_pixels[x, y] = (0, 0, 0, 255)
            
            self.vector_image = rgba_img
            self.vec_frame.config(bg="#e0e0e0")  # Show grayish frame background for transparency preview
            self.vec_canvas.config(bg="#e0e0e0")
        else:
            self.vector_image = bw_img.convert("RGB")
            self.vec_frame.config(bg="#ffffff")
            self.vec_canvas.config(bg="#ffffff")

        # 2. Render Left (Original) Canvas
        self.render_canvas_image(self.orig_canvas, self.original_image, is_original=True)

        # 3. Render Right (Vector Result) Canvas
        self.render_canvas_image(self.vec_canvas, self.vector_image, is_original=False)

    def render_canvas_image(self, canvas, img, is_original=True):
        canvas.update_idletasks()
        cw = canvas.winfo_width()
        ch = canvas.winfo_height()

        if cw <= 10 or ch <= 10:
            cw, ch = 350, 300

        img_copy = img.copy()
        img_copy.thumbnail((cw - 20, ch - 20), Image.Resampling.LANCZOS)

        tk_img = ImageTk.PhotoImage(img_copy)
        
        if is_original:
            self.tk_orig_preview = tk_img
        else:
            self.tk_vec_preview = tk_img

        canvas.delete("all")
        x_off = (cw - img_copy.width) // 2
        y_off = (ch - img_copy.height) // 2
        canvas.create_image(x_off, y_off, anchor="nw", image=tk_img)

    # ---------------------------------------------------------
    # DOWNLOAD / EXPORT LOGIC
    # ---------------------------------------------------------
    def download_file(self):
        selected_fmt = self.export_format_var.get().upper()

        if selected_fmt == "SVG":
            file_path = filedialog.asksaveasfilename(
                title="Save Vector Image",
                defaultextension=".svg",
                filetypes=[("SVG Vector Image", "*.svg"), ("All Files", "*.*")]
            )
            if file_path:
                try:
                    self.export_as_svg(file_path)
                    messagebox.showinfo("Success", f"Vector saved successfully as SVG!\n\nLocation: {file_path}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export SVG:\n{str(e)}")

        elif selected_fmt == "PNG":
            file_path = filedialog.asksaveasfilename(
                title="Save Image",
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")]
            )
            if file_path:
                try:
                    self.vector_image.save(file_path, format="PNG")
                    messagebox.showinfo("Success", f"Image saved successfully as PNG!\n\nLocation: {file_path}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export PNG:\n{str(e)}")

    def export_as_svg(self, output_path):
        """Converts the black line doodle into clean SVG vector path elements."""
        bw_base = self.original_image.convert("L").point(lambda p: 255 if p > 180 else 0)
        width, height = bw_base.size

        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n'
        ]

        # Add white background rect if background removal is false
        if not self.remove_bg_var.get():
            svg_lines.append(f'  <rect width="{width}" height="{height}" fill="#ffffff"/>\n')

        # Run-length vector encoding for black stroke pixels
        pixels = bw_base.load()
        rect_paths = []

        for y in range(height):
            x = 0
            while x < width:
                if pixels[x, y] == 0:  # Black stroke pixel
                    start_x = x
                    while x < width and pixels[x, y] == 0:
                        x += 1
                    rect_paths.append(f'<rect x="{start_x}" y="{y}" width="{x - start_x}" height="1" fill="#000000"/>')
                else:
                    x += 1

        svg_lines.append("  " + "\n  ".join(rect_paths) + "\n</svg>")

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(svg_lines)

    # ---------------------------------------------------------
    # HELPERS & NAVIGATION
    # ---------------------------------------------------------
    def create_dummy_image(self):
        """Generates a fallback doodle for standalone testing."""
        img = Image.new("RGB", (400, 300), color="white")
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([100, 50, 300, 250], outline="black", width=5)
        draw.line([150, 150, 250, 150], fill="black", width=5)
        return img

    def go_back(self):
        if self.controller and hasattr(self.controller, "show_screen3"):
            self.controller.show_screen3()


# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Vector Trace — Screen 4")
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

    screen4 = Screen4Frame(root, controller=None)
    screen4.pack(fill="both", expand=True)

    root.mainloop()