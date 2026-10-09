import cv2


NEIGHBOR_OFFSETS = [
    (-1, -1), (0, -1), (1, -1),
    (-1,  0),          (1,  0),
    (-1,  1), (0,  1), (1, 1)
]


def get_neighbors(point, skeleton):
    x, y = point
    height, width = skeleton.shape

    neighbors = []

    for dx, dy in NEIGHBOR_OFFSETS:
        nx = x + dx
        ny = y + dy

        if 0 <= nx < width and 0 <= ny < height:
            if skeleton[ny, nx] > 0:
                neighbors.append((nx, ny))

    return neighbors


def trace_skeleton_paths(skeleton):
    if skeleton is None:
        raise ValueError(
            "skeleton cannot be None"
        )

    if len(skeleton.shape) != 2:
        raise ValueError(
            "skeleton must be a single-channel image"
        )

    number_of_labels, labels, _, _ = (
        cv2.connectedComponentsWithStats(
            skeleton,
            connectivity=8
        )
    )

    paths = []

    height, width = skeleton.shape

    for label in range(1, number_of_labels):

        component_points = []

        for y in range(skeleton.shape[0]):
            for x in range(skeleton.shape[1]):
                if labels[y, x] == label:
                    component_points.append((x, y))

        if not component_points:
            continue

        remaining = set(component_points)

        while remaining:

            start = next(iter(remaining))

            path = [start]
            remaining.remove(start)

            current = start
            previous = None

            while True:

                neighbors = get_neighbors(
                    current,
                    skeleton
                )

                candidates = [
                    point
                    for point in neighbors
                    if point != previous
                    and point in remaining
                ]

                if not candidates:
                    break

                if previous is None or len(candidates) == 1:
                    next_point = candidates[0]

                else:
                    previous_x, previous_y = previous
                    current_x, current_y = current

                    direction_x = (
                        current_x - previous_x
                    )
                    direction_y = (
                        current_y - previous_y
                    )

                    next_point = min(
                        candidates,
                        key=lambda point: (
                            (
                                point[0]
                                - current_x
                                - direction_x
                            ) ** 2
                            +
                            (
                                point[1]
                                - current_y
                                - direction_y
                            ) ** 2
                        )
                    )

                previous = current
                current = next_point

                path.append(current)
                remaining.remove(current)

            touches_border = any(
                x == 0
                or y == 0
                or x == width - 1
                or y == height - 1
                for x, y in path
            )

            if len(path) >= 5 and not touches_border:
                paths.append(path)

    return paths