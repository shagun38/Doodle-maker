
from email.mime import image
import tkinter as tk
import os
import sys

# Add the src folder to Python's import path
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import the four GUI screens
from GUI.first import FirstPage
from GUI.screen2 import Screen2Frame
from GUI.screen3 import Screen3Frame
from GUI.screen4 import Screen4Frame


class DoodleMakerApp:

    def __init__(self, root):
        self.root = root

        self.root.title("Doodle Maker")
        self.root.geometry("1100x750")
        self.root.minsize(800, 600)

        # Shared application data
        self.image_path = None
        self.original_image = None
        self.adjusted_image = None
        self.processing_result = None

        # Keep track of the current screen
        self.current_screen = None

        # Start with Screen 1
        self.show_screen1()

    def clear_screen(self):
        """Remove the currently displayed screen."""
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_screen1(self):
        print("APP: Opening Screen 1")

        self.clear_screen()

        self.current_screen = FirstPage(
            self.root,
            controller=self
        )

        self.current_screen.pack(fill="both", expand=True)

    def show_screen2(self, image_path=None, image=None):
        print("APP: Opening Screen 2")

        self.clear_screen()

        if image_path is not None:
            self.image_path = image_path

        if image is not None:
            self.original_image = image

        self.processing_result = None
        self.adjusted_image = None

        self.current_screen = Screen2Frame(
            self.root,
            controller=self,
            image_path=self.image_path,
            image=self.original_image
        )

        self.current_screen.pack(fill="both", expand=True)

    def show_screen3(self, image=None, result=None):
        """Display the processing screen."""
        self.clear_screen()

        if image is not None:
            self.adjusted_image = image

        if result is not None:
            self.processing_result = result

        self.current_screen = Screen3Frame(
            self.root,
            controller=self,
            image=self.adjusted_image,
            result=self.processing_result
        )
        self.current_screen.pack(fill="both", expand=True)

    def show_screen4(self, image=None, result=None):
        """Display the final result and export screen."""
        self.clear_screen()

        if image is not None:
            self.adjusted_image = image

        if result is not None:
            self.processing_result = result

        print("DEBUG: Result received by app:", result is not None)
        print("DEBUG: Cached result:", self.processing_result is not None)

        self.current_screen = Screen4Frame(
            self.root,
            controller=self,
            image=self.adjusted_image,
            result=self.processing_result
        )
        self.current_screen.pack(fill="both", expand=True)


def main():
    root = tk.Tk()
    app = DoodleMakerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
