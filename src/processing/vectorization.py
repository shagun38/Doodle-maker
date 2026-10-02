VECTOR_WIDTH =3


def vectorize_paths(paths):
    if paths is None:
        raise ValueError("paths cannot be None")

    vectors = []

    for path in paths:
        if path is None or len(path) < 2:
            continue

        vectors.append({
            "type": "polyline",
            "points": path,
            "width": VECTOR_WIDTH
        })

    return vectors