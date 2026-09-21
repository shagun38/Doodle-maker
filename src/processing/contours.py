import cv2


def detect_contours(mask):
    if mask is None:
        raise ValueError("mask cannot be None")

    if len(mask.shape) != 2:
        raise ValueError("mask must be a single-channel image")

    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    return {
        "contours": contours,
        "hierarchy": hierarchy
    }