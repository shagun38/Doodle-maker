import cv2
from processing.image_input import load_image
from processing.preprocessing import (preprocess_image,suppress_paper_texture)
from processing.extraction import extract_foreground
from processing.cleaning import (remove_small_components)
# from processing.contours import detect_contours
from processing.simplification import simplify_contours
from processing.vectorization import vectorize_contours
# from processing.components import group_vectors
from processing.skeleton import (skeletonize_mask,clean_skeleton , close_mask_gaps)
from processing.path_tracing import (analyze_skeleton, trace_skeleton_paths)


def show_image(window_name, image, max_width=600, max_height=500):
    height, width = image.shape[:2]
    scale = min(max_width / width,max_height / height,1)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = cv2.resize(image,(new_width, new_height))
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.imshow(window_name,resized_image)

image_path = "./test-images/test9.jpeg"

image_data = load_image(image_path)
image = image_data["image"]


preprocessed_data = preprocess_image(image)
# color_image = preprocessed_data["color"]
grayscale_image = preprocessed_data["grayscale"]

# texture_suppressed = suppress_paper_texture(grayscale_image)

extraction_data = extract_foreground(grayscale_image)
mask = extraction_data["mask"]

cleaned_mask = remove_small_components(mask,min_area=100)
closed_mask = close_mask_gaps(cleaned_mask,kernel_size=5)

skeleton = skeletonize_mask(closed_mask)
cleaned_skeleton = clean_skeleton(skeleton,min_component_size=10)
skeleton_data = analyze_skeleton(cleaned_skeleton)

print("Example junctions:",skeleton_data["junctions"][:20])
print(f"Skeleton graph points: "f"{len(skeleton_data['graph'])}")
print(f"Endpoints: "f"{len(skeleton_data['endpoints'])}")
print(f"Normal points: "f"{len(skeleton_data['normal_points'])}")
print(f"Junction pixels: "f"{len(skeleton_data['junctions'])}")
print(f"Junction clusters: "f"{len(skeleton_data['junction_clusters'])}")
print(f"Logical junctions: "f"{len(skeleton_data['logical_junctions'])}")

paths = trace_skeleton_paths(cleaned_skeleton,skeleton_data["graph"],skeleton_data["endpoints"],skeleton_data["logical_junctions"])
print(f"Number of traced paths: {len(paths)}")

if paths:
    print("First path length:", len(paths[0]))
    print("First path:", paths[0][:10])

# paths = trace_skeleton_paths(cleaned_skeleton)
# print(f"Number of paths: {len(paths)}")
# if paths:
#     print("First path:")
#     print(paths[0])

number_of_labels, labels, stats, _ = cv2.connectedComponentsWithStats(cleaned_skeleton,connectivity=8)
print("Skeleton components:",number_of_labels - 1)
show_image("skeleton",skeleton)




# contour_data = detect_contours(cleaned_mask)
# contours = contour_data["contours"]
# contour_image = color_image.copy()
# cv2.drawContours(contour_image,contours,-1,(0, 0, 255),2)

# simplified_contours = simplify_contours(contours)

# print(f"Original contours: {len(contours)}")
# print(f"Simplified contours: {len(simplified_contours)}")
# simplified_image = color_image.copy()

# cv2.drawContours(simplified_image,simplified_contours,-1,(0, 0, 255),2)
# print(f"Number of contours: {len(contours)}")
# simplified_contours = simplify_contours(contours)
# vectors = vectorize_contours(simplified_contours)

# print(f"Number of vectors: {len(vectors)}")
# if vectors:
#     print("First vector:")
#     print(vectors[0])

# components = group_vectors(vectors,max_distance=30)
# print(f"Number of vectors: {len(vectors)}")
# print(f"Number of components: {len(components)}")

# show_image("original image", image)
# show_image("processed color image", color_image)
# show_image("grayscale image", grayscale_image)
# show_image("doodle mask", mask)
# show_image("cleaned mask", cleaned_mask)
# show_image("texture suppressed",texture_suppressed)
# show_image("simplified contours",simplified_image)
# show_image("detected contours", contour_image)

cv2.waitKey(0)
cv2.destroyAllWindows()