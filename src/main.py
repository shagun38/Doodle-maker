import cv2
from processing.image_input import load_image
from processing.preprocessing import preprocess_image
from processing.extraction import extract_foreground

image_path = "./test-images/test7.jpeg"

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
cv2.imshow("original image",image)
cv2.imshow("processed color image",color_image)
cv2.imshow("grayscale image",grayscale_image)

cv2.waitKey(0)
cv2.destroyAllWindows()