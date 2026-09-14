import cv2
def extract_foreground(preprocessed_image):
    # check that a preprocessed image was provided
    if preprocessed_image is None:
        raise ValueError("preprocessed image cannot be none")

    # use otsu's method to automatically determine the threshold
    threshold_value, mask = cv2.threshold(preprocessed_image,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return {
        "mask": mask,
        "threshold": threshold_value
    }