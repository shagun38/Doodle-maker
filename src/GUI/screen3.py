import tkinter as tk
from tkinter import ttk


class Screen3Frame(ttk.Frame):
    def __init__(self, parent, controller=None, image=None):
        super().__init__(parent)
        self.controller = controller
        self.image = image  # Holds the image passed from Screen 2 to pass to Screen 4
        
        self.progress_val = 0
        self.is_animating = True

        self.setup_ui()
        # Start the simulated conversion animation after 300ms
        self.after(300, self.start_processing_animation)

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
            fill="#3bc8fc",  # Accent blue color
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

        # 5. Footer "Please Wait"
        self.wait_label = ttk.Label(
            container,
            text="Please wait...",
            font=("Segoe UI", 10, "italic"),
            foreground="#888888"
        )
        self.wait_label.pack(anchor="center")

    # ---------------------------------------------------------
    # ANIMATION / PROGRESS LOGIC
    # ---------------------------------------------------------
    def update_progress_bar(self, percentage):
        """Updates both the progress bar drawing and percentage text."""
        self.progress_val = min(100, max(0, percentage))
        
        # Calculate pixel width for progress fill
        fill_width = (self.progress_val / 100.0) * self.bar_width
        self.progress_canvas.coords(
            self.progress_rect,
            0, 0, fill_width, self.bar_height
        )
        
        # Update text display
        self.percent_label.config(text=f"{int(self.progress_val)}%")

    def start_processing_animation(self):
        """Simulates conversion through 25% -> 60% -> 72% -> 100%."""
        steps = [
            (25, 400),   # Reach 25% in 400ms
            (60, 600),   # Reach 60% in 600ms
            (72, 500),   # Reach 72% in 500ms
            (100, 600)   # Reach 100% in 600ms
        ]
        self._animate_step(steps, 0)

    def _animate_step(self, steps, step_index):
        if not self.winfo_exists():
            return

        if step_index < len(steps):
            target_pct, duration = steps[step_index]
            start_pct = self.progress_val
            frames = 15
            delay = int(duration / frames)

            def increment(frame=0):
                if frame <= frames:
                    current = start_pct + (target_pct - start_pct) * (frame / frames)
                    self.update_progress_bar(current)
                    self.after(delay, lambda: increment(frame + 1))
                else:
                    # Move to next step
                    self.after(100, lambda: self._animate_step(steps, step_index + 1))

            increment()
        else:
            # Reached 100% — pause briefly then switch to Screen 4
            self.after(400, self.finish_processing)

    def finish_processing(self):
        """Triggers transition to Screen 4."""
        if self.controller and hasattr(self.controller, "show_screen4"):
            self.controller.show_screen4(image=self.image)


# -------------------------------------------------------------
# STANDALONE TEST
# -------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Vector Trace — Screen 3")
    root.geometry("600x500")

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass

    screen3 = Screen3Frame(root, controller=None)
    screen3.pack(fill="both", expand=True)

    root.mainloop()