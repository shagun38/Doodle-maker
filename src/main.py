import cv2
from processing.image_input import load_image
from processing.preprocessing import (preprocess_image,suppress_paper_texture)
from processing.extraction import extract_foreground
from processing.cleaning import (remove_small_components)
from processing.contours import detect_contours

def show_image(window_name, image, max_width=600, max_height=500):
    height, width = image.shape[:2]
    scale = min(max_width / width,max_height / height,1)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = cv2.resize(image,(new_width, new_height))
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.imshow(window_name,resized_image)

image_path = "./test-images/test8.jpeg"

image_data = load_image(image_path)
image = image_data["image"]

# print("image loaded successfully")
# print(f"width = {image_data['width']}")
# print(f"height = {image_data['height']}")
# print(f"channels = {image_data['channels']}")
# print(f"format = {image_data['format']}")

preprocessed_data = preprocess_image(image)
color_image = preprocessed_data["color"]
grayscale_image = preprocessed_data["grayscale"]

texture_suppressed = suppress_paper_texture(grayscale_image)


extraction_data = extract_foreground(grayscale_image)
mask = extraction_data["mask"]

cleaned_mask = remove_small_components(mask,min_area=20)

contour_data = detect_contours(cleaned_mask)
contours = contour_data["contours"]
contour_image = color_image.copy()
cv2.drawContours(contour_image,contours,-1,(0, 0, 255),2)
show_image("detected contours", contour_image)
print(f"Number of contours: {len(contours)}")



# show_image("original image", image)
# show_image("processed color image", color_image)
# show_image("grayscale image", grayscale_image)
# show_image("doodle mask", mask)
#show_image("cleaned mask", cleaned_mask)
show_image("texture suppressed",texture_suppressed)

cv2.waitKey(0)
cv2.destroyAllWindows()