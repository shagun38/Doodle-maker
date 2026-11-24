# VectorTrace — Doodle Maker

Convert a photograph or scan of a hand-drawn doodle into a cleaner, scalable vector-style result.

---

## 1. Project overview

VectorTrace is a computer-graphics project that explores converting hand-drawn artwork into digital vector-style output. The input is a raster image (for example, JPG or PNG). The processing code analyses the image, separates likely foreground strokes from the background, removes small noise components, traces contours, simplifies the resulting point sequences, and exports the result.

The project produces:
- **SVG** — a resolution-independent vector file.
- **PNG** — a raster image exported with an alpha channel by the processing export module.

The central idea is not simply to display a digital copy of a photograph. It is to extract geometric paths from the drawing and represent those paths in a form that can be scaled and edited by vector-graphics software.

### Intended use

- Digitising hand-drawn doodles and simple sketches.
- Creating clean vector-style artwork from raster input.
- Preparing line-art paths for later editing or graphic-design workflows.
- Providing a foundation for future shape recognition, vector editing, or machine-learning extensions.

The current implementation is a classical image-processing pipeline. **It does not train or run a neural network.**

---

## 2. Technology stack

### Programming language
- **Python 3** — application and image-processing logic.

### Libraries used by the processing code

| Library | Purpose |
|---|---|
| OpenCV (`cv2`) | Image loading, filtering, thresholding, connected components, morphology, contour extraction, drawing and PNG writing |
| NumPy | Image arrays, coordinate arrays and numerical operations |
| SciPy | B-spline fitting and curve sampling in path simplification |
| Pillow (`PIL`) | GUI image loading, image enhancement, preview rendering and PNG saving |
| Tkinter | Desktop GUI widgets, windows, dialogs and navigation |

### Packages listed in `requirements.txt`

The supplied `requirements.txt` contains:

```text
opencv-contrib-python
numpy
scipy
PyOpenGL
matplotlib
Pillow
```

**Dependency note:** The source code imports OpenCV, NumPy, SciPy, Pillow and Python's built-in Tkinter. `PyOpenGL` and `matplotlib` are listed in the supplied requirements file but are not imported by the inspected project source. Tkinter is part of many standard Python installations, but on some Linux systems it must be installed separately through the operating system's package manager.

`opencv-contrib-python` is important because the skeletonization utility calls `cv2.ximgproc.thinning`, which is provided by the contrib build.

---

## 3. Repository structure

```text
Doodle-maker/
│
├── README.md
├── requirements.txt
│
└── src/
    ├── main.py
    ├── final_doodle.svg
    ├── final_doodle.png
    │
    ├── processing/
    │   ├── __init__.py
    │   ├── image_input.py
    │   ├── preprocessing.py
    │   ├── extraction.py
    │   ├── cleaning.py
    │   ├── skeleton.py
    │   ├── path_tracing.py
    │   ├── simplification.py
    │   ├── vectorization.py
    │   ├── rendering.py
    │   └── export.py
    │
    ├── gui/
    │   ├── first.py
    │   ├── screen2.py
    │   ├── screen3.py
    │   └── screen4.py
    │
    └── test-images/
        └── sample input images
```

---

## 4. Requirements

### Software

- Python 3.9 or newer is recommended.
- pip (Python package installer).
- A desktop environment for Tkinter windows.
- Tkinter support in the Python installation.

The exact minimum Python version has not been declared by the repository. Python 3.9+ is a practical recommendation, not a verified project constraint.

### Input image formats

The processing image loader accepts:

- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.webp`

The loader rejects images wider or taller than **4096 pixels**.


---

## 5. Installation and setup

### Step 1 — Extract the ZIP

Extract the project archive to a folder, for example:

```text
Doodle-maker/
```

Open a terminal or command prompt in that extracted folder.

### Step 2 — Create a virtual environment (recommended)

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install the dependencies

From the project root, run:

```bash
pip install -r requirements.txt
```

If Tkinter is missing on Linux, install the Tkinter package using the distribution's package manager. For example, on Debian/Ubuntu-based systems:

```bash
sudo apt install python3-tk
```

### Step 4 — Verify imports

You can check the main libraries with:

```bash
python -c "import cv2, numpy, scipy; from PIL import Image; print('Core imports OK')"
```

Check the contrib thinning feature, if you intend to use skeletonization:

```bash
python -c "import cv2; print(hasattr(cv2, 'ximgproc'))"
```

If this prints `False`, check that the contrib OpenCV package is installed and that a conflicting OpenCV package is not installed in the same environment.

---

## 7. How to run the processing pipeline

The current script uses a test image path relative to the `src` directory:

```python
image_path = "./test-images/test8.jpeg"
```

Therefore, run it from inside `src`.

### Windows

```bash
cd src
python main.py
```

### macOS / Linux

```bash
cd src
python3 main.py
```

The script will:
1. Load `test-images/test8.jpeg`.
2. Preprocess the image.
3. Extract a foreground mask.
4. Remove small connected components.
5. Close small gaps in the mask.
6. Trace contours and simplify the paths.
7. Convert paths into polyline vector records.
8. Render a preview in an OpenCV window.
9. Save `final_doodle.svg` and `final_doodle.png` in the current working directory (normally `src/` when run as shown).

Close the preview window to let the script finish.


---

## 7. How the system works

The processing pipeline follows this sequence:

```text
Input image
    |
    v
Image loading and validation
    |
    v
Preprocessing
(denoising + illumination correction + grayscale)
    |
    v
Foreground extraction
(adaptive thresholding)
    |
    v
Noise removal
(connected-component filtering)
    |
    v
Gap closing
(morphological closing)
    |
    v
Contour / path tracing
    |
    v
Path simplification
(RDP + optional B-spline smoothing)
    |
    v
Vectorization
(polyline records)
    |
    +----------------------+
    |                      |
    v                      v
Preview rendering       File export
                         SVG + PNG
```

---

## 12. Output files

When `src/main.py` is run from the `src` directory, it writes:

| Output | Description |
|---|---|
| `final_doodle.svg` | SVG file containing closed path geometry |
| `final_doodle.png` | RGBA PNG created by filling exported contours |

The archive already includes files with these names. Running the script again may overwrite them in the current working directory.

The GUI Screen 4 uses a save dialog and lets the user choose a destination and file name.

---

## 15. Does this project use machine learning?

**No. The current implementation does not train a machine-learning model.**

It uses traditional computer-vision and geometry techniques implemented with OpenCV, NumPy and SciPy. These methods are algorithmic: they process pixel intensity, connected regions, contours and coordinate paths.

A future version could use machine learning for tasks such as doodle classification, semantic recognition, or learning to reconstruct stylized strokes. Those capabilities are not part of the current code in this archive.

---

## 16. Quick start

For a quick run after installing dependencies:

```bash
# From the project root
pip install -r requirements.txt

# Enter the source directory because main.py uses a relative image path
cd src

# Run the processing pipeline
python main.py
```

Expected result:
- An OpenCV preview window.
- `final_doodle.svg`
- `final_doodle.png`

---

## 17. Project summary

VectorTrace is a Python-based computer-graphics project that converts raster doodle images into vector-style representations. Its processing pipeline combines image enhancement, adaptive thresholding, connected-component filtering, morphological operations, contour extraction, path simplification, spline smoothing, polyline representation and SVG/PNG export.

The repository also contains a Tkinter GUI prototype for image upload, cropping, contrast adjustment, progress display and result export. The next major engineering step is to integrate this interface with the main processing pipeline so that the user-facing application and the underlying vectorization code operate as one end-to-end system.

---

