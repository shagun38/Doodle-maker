import cv2


def preprocess_image(image):
    if image is None:
        raise ValueError("image cannot be none")

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # reduce small amounts of image noise
    blurred = cv2.GaussianBlur(
        grayscale,
        (5, 5),
        0
    )

    # create a clahe object for local contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(blurred)

    return enhanced