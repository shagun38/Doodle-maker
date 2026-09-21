import cv2


def detect_contours(mask, min_contour_area=50):
    if mask is None:
        raise ValueError("mask cannot be None")

    if len(mask.shape) != 2:
        raise ValueError("mask must be a single-channel image")

    contours, hierarchy = cv2.findContours(
        mask,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    filtered_contours = []

    for contour in contours:
        area = cv2.contourArea(contour)

        if area >= min_contour_area:
            filtered_contours.append(contour)

    return {
        "contours": filtered_contours,
        "hierarchy": hierarchy
    }