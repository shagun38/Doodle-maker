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


def build_skeleton_graph(skeleton):
    if skeleton is None:
        raise ValueError("skeleton cannot be None")

    if len(skeleton.shape) != 2:
        raise ValueError(
            "skeleton must be a single-channel image"
        )

    graph = {}

    height, width = skeleton.shape

    for y in range(height):
        for x in range(width):

            if skeleton[y, x] == 0:
                continue

            point = (x, y)

            neighbors = get_neighbors(
                point,
                skeleton
            )

            graph[point] = neighbors

    return graph


def classify_graph_points(graph):
    endpoints = []
    normal_points = []
    junctions = []

    for point, neighbors in graph.items():
        degree = len(neighbors)

        if degree == 1:
            endpoints.append(point)

        elif degree == 2:
            normal_points.append(point)

        elif degree >= 3:
            junctions.append(point)

    return {
        "endpoints": endpoints,
        "normal_points": normal_points,
        "junctions": junctions
    }


def analyze_skeleton(skeleton):
    graph = build_skeleton_graph(skeleton)

    classification = classify_graph_points(graph)

    junction_clusters = cluster_junctions(
        classification["junctions"]
    )

    logical_junctions = merge_nearby_junctions(
        junction_clusters,
        merge_distance=10
    )

    return {
        "graph": graph,
        "endpoints": classification["endpoints"],
        "normal_points": classification["normal_points"],
        "junctions": classification["junctions"],
        "junction_clusters": junction_clusters,
        "logical_junctions": logical_junctions
    }

def cluster_junctions(junctions):
    if junctions is None:
        raise ValueError("junctions cannot be None")

    junctions = set(junctions)
    clusters = []

    while junctions:
        start = junctions.pop()

        cluster = {start}
        stack = [start]

        while stack:
            current = stack.pop()

            x, y = current

            nearby = []

            for dx, dy in NEIGHBOR_OFFSETS:
                neighbor = (x + dx, y + dy)

                if neighbor in junctions:
                    nearby.append(neighbor)

            for neighbor in nearby:
                junctions.remove(neighbor)
                cluster.add(neighbor)
                stack.append(neighbor)

        clusters.append(cluster)

    return clusters

def get_cluster_center(cluster):
    if not cluster:
        return None

    x_sum = sum(point[0] for point in cluster)
    y_sum = sum(point[1] for point in cluster)

    center_x = x_sum / len(cluster)
    center_y = y_sum / len(cluster)

    return min(
        cluster,
        key=lambda point: (
            (point[0] - center_x) ** 2
            + (point[1] - center_y) ** 2
        )
    )


def merge_nearby_junctions(
    junction_clusters,
    merge_distance=10
):
    if junction_clusters is None:
        raise ValueError(
            "junction_clusters cannot be None"
        )

    if not junction_clusters:
        return []

    centers = [
        get_cluster_center(cluster)
        for cluster in junction_clusters
    ]

    merged = []
    visited = set()

    for i in range(len(junction_clusters)):

        if i in visited:
            continue

        stack = [i]
        visited.add(i)

        merged_clusters = []

        while stack:
            current = stack.pop()

            merged_clusters.append(
                junction_clusters[current]
            )

            current_center = centers[current]

            for j in range(len(junction_clusters)):

                if j in visited:
                    continue

                other_center = centers[j]

                dx = (
                    current_center[0]
                    - other_center[0]
                )

                dy = (
                    current_center[1]
                    - other_center[1]
                )

                distance = (dx * dx + dy * dy) ** 0.5

                if distance <= merge_distance:
                    visited.add(j)
                    stack.append(j)

        merged_pixels = set()

        for cluster in merged_clusters:
            merged_pixels.update(cluster)

        merged.append({
            "pixels": merged_pixels,
            "center": get_cluster_center(
                merged_pixels
            )
        })

    return merged


def get_logical_junction_map(logical_junctions):
    junction_map = {}

    for index, junction in enumerate(logical_junctions):
        for point in junction["pixels"]:
            junction_map[point] = index

    return junction_map


def get_graph_nodes(
    graph,
    endpoints,
    logical_junctions
):
    nodes = set(endpoints)

    for junction in logical_junctions:
        nodes.add(junction["center"])

    return nodes


def trace_path(
    start,
    first_neighbor,
    graph,
    node_map,
    visited_edges
):
    path = [start, first_neighbor]

    previous = start
    current = first_neighbor

    while True:

        edge = tuple(sorted((previous, current)))
        visited_edges.add(edge)

        if current in node_map and current != start:
            break

        neighbors = graph.get(current, [])

        next_points = [
            point
            for point in neighbors
            if point != previous
            and tuple(sorted((current, point)))
            not in visited_edges
        ]

        if not next_points:
            break

        next_point = next_points[0]

        previous = current
        current = next_point

        path.append(current)

    return path

def build_junction_pixel_map(logical_junctions):
    junction_map = {}

    for junction_id, junction in enumerate(logical_junctions):
        for pixel in junction["pixels"]:
            junction_map[pixel] = junction_id

    return junction_map

def trace_path_from_node(
    start,
    first_neighbor,
    graph,
    junction_map,
    endpoint_set,
    visited_edges
):
    path = [start]

    previous = start
    current = first_neighbor

    while True:
        path.append(current)

        edge = tuple(sorted((previous, current)))
        visited_edges.add(edge)

        # Stop when we reach another logical junction.
        if current in junction_map:
            break

        # Stop when we reach an endpoint.
        if current in endpoint_set:
            break

        neighbors = graph.get(current, [])

        next_points = []

        for neighbor in neighbors:
            edge = tuple(sorted((current, neighbor)))

            if neighbor != previous and edge not in visited_edges:
                next_points.append(neighbor)

        if not next_points:
            break

        # A normal skeleton point should have one
        # forward direction.
        next_point = next_points[0]

        previous = current
        current = next_point

    return path

def trace_skeleton_paths(
    skeleton,
    graph,
    endpoints,
    logical_junctions
):
    if skeleton is None:
        raise ValueError("skeleton cannot be None")

    junction_map = build_junction_pixel_map(
        logical_junctions
    )

    endpoint_set = set(endpoints)

    visited_edges = set()
    paths = []

    # --------------------------------------------------
    # Phase 1: endpoint -> junction/endpoint
    # --------------------------------------------------

    for start in endpoints:

        neighbors = graph.get(start, [])

        for neighbor in neighbors:

            edge = tuple(sorted((start, neighbor)))

            if edge in visited_edges:
                continue

            path = trace_path_from_node(
                start,
                neighbor,
                graph,
                junction_map,
                endpoint_set,
                visited_edges
            )

            if len(path) >= 2:
                paths.append(path)

    # --------------------------------------------------
    # Phase 2: junction -> junction/endpoint
    # --------------------------------------------------

    for junction in logical_junctions:

        for start in junction["pixels"]:

            neighbors = graph.get(start, [])

            for neighbor in neighbors:

                edge = tuple(sorted((start, neighbor)))

                if edge in visited_edges:
                    continue

                path = trace_path_from_node(
                    start,
                    neighbor,
                    graph,
                    junction_map,
                    endpoint_set,
                    visited_edges
                )

                if len(path) >= 2:
                    paths.append(path)

    return paths