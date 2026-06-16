import cv2
import numpy as np
import math
from typing import List, Dict

from app.core.pdi.region_detection import BlobRegion

DIRECTIONS_8 = [
    "top", "top-right", "right", "bottom-right",
    "bottom", "bottom-left", "left", "top-left",
]


def _angle_to_direction(dx: float, dy: float) -> str:
    angle = math.degrees(math.atan2(-dy, dx))
    if angle < 0:
        angle += 360
    sectors = [
        (337.5, 22.5, "right"),
        (22.5, 67.5, "bottom-right"),
        (67.5, 112.5, "bottom"),
        (112.5, 157.5, "bottom-left"),
        (157.5, 202.5, "left"),
        (202.5, 247.5, "top-left"),
        (247.5, 292.5, "top"),
        (292.5, 337.5, "top-right"),
    ]
    for low, high, direction in sectors:
        if low <= angle < high:
            return direction
    return "right"


def _compute_overlap(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    intersection = cv2.bitwise_and(mask_a, mask_b)
    inter_pixels = float(cv2.countNonZero(intersection))
    if inter_pixels == 0:
        return 0.0
    area_a = float(cv2.countNonZero(mask_a))
    area_b = float(cv2.countNonZero(mask_b))
    min_area = min(area_a, area_b)
    if min_area == 0:
        return 0.0
    return inter_pixels / min_area


def compute_region_relationships(
    regions: List[BlobRegion],
) -> Dict[str, dict]:
    relationships: Dict[str, dict] = {}

    for region in regions:
        relationships[region.region_id] = {
            "overlaps_with": [],
            "proximity_to": [],
            "layer_order": 0,
        }

    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            r_a = regions[i]
            r_b = regions[j]

            overlap = _compute_overlap(r_a.mask, r_b.mask)
            overlap_threshold = 0.7

            if overlap > overlap_threshold:
                relationships[r_a.region_id]["overlaps_with"].append(r_b.region_id)
                relationships[r_b.region_id]["overlaps_with"].append(r_a.region_id)

            cx_a, cy_a = r_a.centroid
            cx_b, cy_b = r_b.centroid
            dx = cx_b - cx_a
            dy = cy_b - cy_a
            distance = math.sqrt(dx ** 2 + dy ** 2)
            direction = _angle_to_direction(dx, dy)

            relationships[r_a.region_id]["proximity_to"].append({
                "region_id": r_b.region_id,
                "distance_px": round(distance, 2),
                "direction": direction,
            })
            relationships[r_b.region_id]["proximity_to"].append({
                "region_id": r_a.region_id,
                "distance_px": round(distance, 2),
                "direction": _angle_to_direction(-dx, -dy),
            })

    for region in regions:
        cy = region.centroid[1]
        relationships[region.region_id]["layer_order"] = int(cy)

    return relationships
