import cv2
import numpy as np

from processing.image_input import load_image
from processing.preprocessing import preprocess_image
from processing.extraction import extract_foreground
from processing.cleaning import remove_small_components
from processing.skeleton import close_mask_gaps, skeletonize_mask
from processing.path_tracing import trace_skeleton_paths
from processing.simplification import simplify_paths
from processing.vectorization import vectorize_paths
from processing.rendering import render_vectors

def show_image(window_name,image,max_width=1200,max_height=800):
    height, width = image.shape[:2]
    scale = min(max_width / width,max_height / height,1)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = cv2.resize(image,(new_width, new_height),interpolation=cv2.INTER_NEAREST)

    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.imshow(window_name,resized_image)




# -------------------------
# Input
# -------------------------
image_path = "./test-images/test1.jpeg"
image_data = load_image(image_path)
image = image_data["image"]

# -------------------------
# Preprocessing
# -------------------------

preprocessed_data = preprocess_image(image)
grayscale_image = preprocessed_data["grayscale"]

# -------------------------
# extract foreground
# -------------------------

extraction_data = extract_foreground(grayscale_image)
mask = extraction_data["mask"]

# -------------------------
# clean mask
# -------------------------
cleaned_mask = remove_small_components(mask,min_area=100)

# -------------------------
# close gaps
# -------------------------
closed_mask = close_mask_gaps(cleaned_mask,kernel_size=5)

# -------------------------
# Skeletonization
# -------------------------

skeleton = skeletonize_mask(closed_mask)

# -------------------------
# path tracking
# -------------------------
paths = trace_skeleton_paths(skeleton)
simplified_paths = simplify_paths(paths,epsilon_ratio=0.01)

# -------------------------
# Vectorization
# -------------------------

vectors = vectorize_paths(simplified_paths)

# -------------------------
# Rendering
# -------------------------
vector_image = render_vectors(vectors,image_data["width"],image_data["height"])

show_image("vector output",vector_image)

cv2.waitKey(0)
cv2.destroyAllWindows()