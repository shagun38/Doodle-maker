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


def count_components(image):
    number_of_labels, _, _, _ = (
        cv2.connectedComponentsWithStats(image,connectivity=8))
    return number_of_labels - 1


def count_components_with_connectivity(image, connectivity):
    number_of_labels, _, _, _ = (cv2.connectedComponentsWithStats(image,connectivity=connectivity))
    return number_of_labels - 1


def count_diagonal_only_pixels(skeleton):
    height, width = skeleton.shape
    count = 0

    for y in range(height):
        for x in range(width):
            if skeleton[y, x] == 0:
                continue

            orthogonal_neighbors = 0
            diagonal_neighbors = 0

            for dx, dy in [(0, -1),(-1, 0),(1, 0),(0, 1)]:
                nx = x + dx
                ny = y + dy

                if (0 <= nx < width and 0 <= ny < height and skeleton[ny, nx] > 0):
                    orthogonal_neighbors += 1

            for dx, dy in [(-1, -1),(1, -1),(-1, 1),(1, 1)]:
                nx = x + dx
                ny = y + dy

                if (0 <= nx < width and 0 <= ny < height and skeleton[ny, nx] > 0):
                    diagonal_neighbors += 1

            if (orthogonal_neighbors == 0 and diagonal_neighbors > 0):
                count += 1

    return count





image_path = "./test-images/test10.jpeg"

# -------------------------
# Input
# -------------------------

image_data = load_image(image_path)
image = image_data["image"]

# -------------------------
# Preprocessing
# -------------------------

preprocessed_data = preprocess_image(image)
grayscale_image = preprocessed_data["grayscale"]

# -------------------------
# Foreground extraction
# -------------------------

extraction_data = extract_foreground(grayscale_image)
mask = extraction_data["mask"]

# -------------------------
# Cleaning
# -------------------------
cleaned_mask = remove_small_components(mask,min_area=100)

# -------------------------
# Gap closing
# -------------------------
closed_mask = close_mask_gaps(cleaned_mask,kernel_size=5)

# -------------------------
# Skeletonization
# -------------------------

skeleton = skeletonize_mask(closed_mask)
paths = trace_skeleton_paths(skeleton)
path_image = cv2.cvtColor(skeleton,cv2.COLOR_GRAY2BGR)
for path in paths:
    points = np.array(path,dtype=np.int32)
    cv2.polylines(path_image,[points],False,(0, 255, 0),thickness=2,lineType=cv2.LINE_AA)

show_image("traced paths",path_image)

traced_pixels = set()
for path in paths:
    for point in path:
        traced_pixels.add(tuple(point))

skeleton_pixels = {
    (x, y)
    for y, x in zip(
        *np.where(skeleton > 0))
}

untraced_pixels = (skeleton_pixels - traced_pixels)
untraced_image = np.zeros_like(path_image)

# Start with skeleton in white
untraced_image[
    skeleton > 0
] = (255, 255, 255)

# Traced pixels in green
for x, y in traced_pixels:
    untraced_image[y, x] = (0, 255, 0)

# Untraced pixels in red
for x, y in untraced_pixels:
    untraced_image[y, x] = (0, 0, 255)

# show_image(
#     "traced vs untraced",
#     untraced_image
# )

skeleton_pixels = set(
    zip(
        *np.where(skeleton > 0)
    )
)

skeleton_pixels = {
    (x, y)
    for y, x in skeleton_pixels
}

untraced_pixels = (skeleton_pixels - traced_pixels)
# print("Skeleton pixels:",len(skeleton_pixels))
# print("Traced pixels:",len(traced_pixels))
# print("Untraced skeleton pixels:",len(untraced_pixels))
# -------------------------
# Check skeleton
# -------------------------
# show_image("skeleton",skeleton)

simplified_paths = simplify_paths(paths,epsilon_ratio=0.01)

# print("Original paths:", len(paths))
# print("Simplified paths:", len(simplified_paths))

# for index, path in enumerate(simplified_paths[:10]):
#     print(
#         f"Path {index}: "
#         f"{len(paths[index])} -> {len(path)} points"
#     )

simplified_image = cv2.cvtColor(
    skeleton,
    cv2.COLOR_GRAY2BGR
)

for path in simplified_paths:
    points = np.array(
        path,
        dtype=np.int32
    )

    cv2.polylines(
        simplified_image,
        [points],
        False,
        (0, 255, 0),
        thickness=2,
        lineType=cv2.LINE_AA
    )

# show_image(
#     "simplified paths",
#     simplified_image
# )


vectors = vectorize_paths(
    simplified_paths
)

print("Vector paths:", len(vectors))

for index, vector in enumerate(vectors[:10]):
    print(
        f"Vector {index}: "
        f"{vector['type']}, "
        f"{len(vector['points'])} points, "
        f"width={vector['width']}"
    )


vectors = vectorize_paths(
    simplified_paths
)
vector_image = render_vectors(
    vectors,
    image_data["width"],
    image_data["height"]
)

show_image(
    "vector output",
    vector_image
)

cv2.waitKey(0)
cv2.destroyAllWindows()