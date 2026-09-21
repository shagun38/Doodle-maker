import cv2


def simplify_contours(contours, epsilon_ratio=0.01):
    if contours is None:
        raise ValueError("contours cannot be None")

    simplified_contours = []

    for contour in contours:
        if len(contour) < 3:
            continue

        perimeter = cv2.arcLength(contour, True)

        epsilon = 0.01

        simplified = cv2.approxPolyDP(
            contour,
            epsilon,
            True
        )

        simplified_contours.append(simplified)

    return simplified_contours