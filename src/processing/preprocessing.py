import cv2
import numpy as np


def preprocess_image(image):
    if image is None:
        raise ValueError("image cannot be none")

    # apply a small blur to reduce camera noise
    denoised = cv2.GaussianBlur(image,(3, 3),0)
    hsv = cv2.cvtColor(denoised,cv2.COLOR_BGR2HSV)
    value = hsv[:, :, 2]
    illumination = cv2.GaussianBlur(value,(0, 0),25)

    illumination = np.maximum(illumination,1)
    corrected_value = (value.astype(np.float32) /illumination.astype(np.float32))

    # normalize the corrected brightness to 0-255
    corrected_value = cv2.normalize(corrected_value,None,0,255,cv2.NORM_MINMAX)
    corrected_value = corrected_value.astype(np.uint8)

    # replace the original value channel
    corrected_hsv = hsv.copy()
    corrected_hsv[:, :, 2] = corrected_value

    # convert corrected hsv image back to bgr
    corrected_color = cv2.cvtColor(corrected_hsv,cv2.COLOR_HSV2BGR)
    corrected_grayscale = cv2.cvtColor(corrected_color,cv2.COLOR_BGR2GRAY)

    return {
        "original": image,
        "color": corrected_color,
        "grayscale": corrected_grayscale
    }

def suppress_paper_texture(gray):
    if gray is None:
        raise ValueError("gray image cannot be None")
    background = cv2.GaussianBlur(gray,(0, 0),sigmaX=15)
    normalized = cv2.divide(gray,background,scale=255)

    return normalized