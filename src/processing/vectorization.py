def vectorize_contours(contours):
    if contours is None:
        raise ValueError("contours cannot be None")

    vectors = []

    for contour in contours:
        if contour is None or len(contour) < 2:
            continue

        points = contour.reshape(-1, 2)

        vector = {
            "type": "polyline",
            "points": points.tolist(),
            "closed": True
        }

        vectors.append(vector)

    return vectors