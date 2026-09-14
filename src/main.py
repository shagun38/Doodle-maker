import cv2
from processing.image_input import load_image
from processing.preprocessing import preprocess_image
from processing.extraction import extract_foreground

image_path = "test1.jpeg"

image_data = load_image(image_path)
image = image_data["image"]

# print("image loaded successfully")
# print(f"width = {image_data['width']}")
# print(f"height = {image_data['height']}")
# print(f"channels = {image_data['channels']}")
# print(f"format = {image_data['format']}")

preprocessed_image = preprocess_image(image)



extraction_data = extract_foreground(preprocessed_image)
# get the binary mask
mask = extraction_data["mask"]
threshold = extraction_data["threshold"]

print(f"otsu threshold = {threshold}")

# cv2.imshow("original image",image)
# cv2.imshow("preprocessed image",preprocessed_image)
cv2.imshow("foreground mask",mask)
cv2.waitKey(0)
cv2.destroyAllWindows()