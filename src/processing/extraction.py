# extraction.py

import cv2


def extract_foreground(grayscale_image):
    if grayscale_image is None:
        raise ValueError("grayscale image cannot be none")

    if len(grayscale_image.shape) != 2:
        raise ValueError(
            "extract_foreground expects a grayscale image"
        )

    block_size = 31
    constant = 10

    # create the foreground mask
    mask = cv2.adaptiveThreshold(grayscale_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,block_size,constant)

    # return the mask and parameters used
    return {
        "mask": mask,
        "block_size": block_size,
        "constant": constant
    }