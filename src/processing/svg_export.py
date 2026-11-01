
from pathlib import Path
import math


def export_svg(vectors, width, height, output_path, transparent=False):
    """Export traced polylines as genuine SVG vector elements."""

    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive.")

    elements = []

    if not transparent:
        elements.append(
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>'
        )

    for vector in vectors:
        points = vector.get("points")
        stroke_width = vector.get("width", 3)

        if not points or len(points) < 2:
            continue

        stroke_width = float(stroke_width)
        if not math.isfinite(stroke_width) or stroke_width <= 0:
            continue

        coords = []
        for point in points:
            x, y = float(point[0]), float(point[1])

            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Invalid vector coordinates.")

            coords.append(f"{x:g},{y:g}")

        elements.append(
            f'<polyline points="{" ".join(coords)}" '
            f'fill="none" stroke="#000000" '
            f'stroke-width="{stroke_width:g}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        + "\n".join(elements)
        + "\n</svg>\n"
    )

    Path(output_path).write_text(svg, encoding="utf-8")
