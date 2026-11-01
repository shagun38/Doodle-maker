import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageFilter
from PIL import ImageDraw
from Integration.pipeline import process_pil_image
from processing.svg_export import export_svg



class Screen4Frame(ttk.Frame):

    def __init__(self, parent, controller=None, image=None, result=None):
        super().__init__(parent)
        self.controller = controller

        self.original_image = (
            image if image is not None else self.create_dummy_image()
        )
        self.pipeline_result = result
        self.vector_image = None

        self.tk_orig_preview = None
        self.tk_vec_preview = None

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

        try:
            # Run the actual vectorization pipeline once.
            if self.pipeline_result is None:
                self.pipeline_result = process_pil_image(
                    self.original_image
                )

            result = self.pipeline_result

            if self.remove_bg_var.get():
                # Draw the actual vector paths on a transparent canvas.
                transparent = Image.new(
                    "RGBA",
                    (result["width"], result["height"]),
                    (0, 0, 0, 0),
                )
                draw = ImageDraw.Draw(transparent)

                for vector in result["vectors"]:
                    points = vector.get("points", [])
                    width = max(1, round(vector.get("width", 3)))

                    if len(points) >= 2:
                        draw.line(
                            [tuple(point) for point in points],
                            fill=(0, 0, 0, 255),
                            width=width,
                            joint="curve",
                        )

                self.vector_image = transparent
                self.vec_canvas.config(bg="#e0e0e0")
            else:
                self.vector_image = result["preview"].copy()
                self.vec_canvas.config(bg="#ffffff")

            self.render_canvas_image(
                self.orig_canvas,
                self.original_image,
                is_original=True,
            )
            self.render_canvas_image(
                self.vec_canvas,
                self.vector_image,
                is_original=False,
            )

        except Exception as exc:
            messagebox.showerror(
                "Processing Error",
                f"Could not process the image:\n{exc}",
            )

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
        if self.pipeline_result is None:
            raise ValueError(
                "Please process the image before exporting."
            )

        result = self.pipeline_result

        export_svg(
            vectors=result["vectors"],
            width=result["width"],
            height=result["height"],
            output_path=output_path,
            transparent=self.remove_bg_var.get(),
        )

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