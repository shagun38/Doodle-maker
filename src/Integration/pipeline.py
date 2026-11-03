
import cv2
import numpy as np
from PIL import Image

from processing.preprocessing import preprocess_image
from processing.extraction import extract_foreground
from processing.cleaning import remove_small_components
from processing.skeleton import close_mask_gaps, skeletonize_mask
from processing.path_tracing import trace_skeleton_paths
from processing.simplification import simplify_paths
from processing.vectorization import vectorize_paths
from processing.rendering import render_vectors


def process_pil_image(pil_image, progress_callback=None):
    """Process a PIL image and optionally report processing progress."""

    def report_progress(stage, percentage):
        if progress_callback:
            progress_callback(stage, percentage)

    if pil_image is None:
        raise ValueError("Please provide an image.")

    report_progress("Preparing image", 0)

    rgb = np.array(pil_image.convert("RGB"))
    image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    height, width = image.shape[:2]

    if width > 4096 or height > 4096:
        raise ValueError("Maximum supported image dimensions are 4096x4096.")

    # 1. Preprocessing
    preprocessed = preprocess_image(image)
    grayscale = preprocessed["grayscale"]
    report_progress("Preprocessing completed", 10)

    # 2. Foreground extraction
    extraction = extract_foreground(grayscale)
    mask = extraction["mask"]
    report_progress("Foreground extraction completed", 25)

    # 3. Cleaning
    cleaned = remove_small_components(mask, min_area=100)
    closed = close_mask_gaps(cleaned, kernel_size=5)
    report_progress("Image cleaning completed", 40)

    # 4. Skeletonization
    skeleton = skeletonize_mask(closed)
    report_progress("Skeletonization completed", 55)

    # 5. Path tracing
    paths = trace_skeleton_paths(skeleton)
    report_progress("Path tracing completed", 70)

    # 6. Path simplification
    simplified = simplify_paths(paths, max_deviation=0.5)
    report_progress("Path simplification completed", 80)

    # 7. Vectorization
    vectors = vectorize_paths(simplified)
    report_progress("Vectorization completed", 90)

    # 8. Rendering
    rendered = render_vectors(vectors, width, height)

    # Convert black background / white strokes
    # into white background / black strokes.
    rendered = cv2.bitwise_not(rendered)

    preview_rgb = cv2.cvtColor(rendered, cv2.COLOR_BGR2RGB)

    result = {
        "preview": Image.fromarray(preview_rgb),
        "vectors": vectors,
        "width": width,
        "height": height,
    }

    report_progress("Processing completed", 100)

    return result
