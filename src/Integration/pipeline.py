
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


def process_pil_image(pil_image):
    """Process the image supplied by the Tkinter GUI."""

    if pil_image is None:
        raise ValueError("Please provide an image.")

    rgb = np.array(pil_image.convert("RGB"))
    image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    height, width = image.shape[:2]

    if width > 4096 or height > 4096:
        raise ValueError("Maximum supported image dimensions are 4096x4096.")

    preprocessed = preprocess_image(image)
    grayscale = preprocessed["grayscale"]

    extraction = extract_foreground(grayscale)
    mask = extraction["mask"]

    cleaned = remove_small_components(mask, min_area=100)
    closed = close_mask_gaps(cleaned, kernel_size=5)
    skeleton = skeletonize_mask(closed)

    paths = trace_skeleton_paths(skeleton)
    simplified = simplify_paths(paths, max_deviation=0.5)
    vectors = vectorize_paths(simplified)

    # Existing renderer: black background, white vector strokes.
    rendered = render_vectors(vectors, width, height)

    # GUI output: white background, black vector strokes.
    rendered = cv2.bitwise_not(rendered)
    preview_rgb = cv2.cvtColor(rendered, cv2.COLOR_BGR2RGB)

    return {
        "preview": Image.fromarray(preview_rgb),
        "vectors": vectors,
        "width": width,
        "height": height,
    }
