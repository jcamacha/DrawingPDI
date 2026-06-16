import cv2
import numpy as np
import math
from typing import Tuple

from app.core.pdi.segmentation import (
    compute_color_distribution,
    compute_color_histogram,
    compute_vad_from_histogram,
    COLOR_RANGES_HSV,
)
from app.core.pdi.edges import apply_canny_edge_detection, compute_stroke_metrics
from app.core.pdi.region_detection import BlobRegion


def _compute_compactness(mask: np.ndarray, polygon: np.ndarray) -> float:
    area = float(cv2.countNonZero(mask))
    if area == 0:
        return 0.0
    if polygon.size == 0:
        return 0.0
    perimeter = float(cv2.arcLength(polygon, True))
    if perimeter == 0:
        return 0.0
    compactness = (4.0 * math.pi * area) / (perimeter ** 2)
    return round(min(compactness, 1.0), 4)


def _find_dominant_color_in_region(image: np.ndarray, mask: np.ndarray) -> str:
    dist = compute_color_distribution(image, mask=mask)
    specific = dist["specific"]
    color_map = {
        "red_pct": "red",
        "orange_pct": "orange",
        "yellow_pct": "yellow",
        "green_pct": "green",
        "blue_pct": "blue",
        "violet_pct": "violet",
        "white_pct": "white",
        "black_pct": "black",
        "gray_pct": "gray",
    }
    max_pct = 0.0
    dominant = "unknown"
    for key, name in color_map.items():
        pct = specific.get(key, 0.0)
        if pct > max_pct:
            max_pct = pct
            dominant = name
    return dominant


def compute_region_metrics(
    image: np.ndarray,
    blob: BlobRegion,
) -> dict:
    mask = blob.mask

    if cv2.countNonZero(mask) == 0:
        return {
            "color_distribution": {
                "specific": {k: 0.0 for k in [
                    "red_pct", "orange_pct", "yellow_pct", "green_pct",
                    "blue_pct", "violet_pct", "white_pct", "black_pct",
                    "gray_pct", "other_pct",
                ]},
                "therapeutic_groups": {
                    "warm_pct": 0.0, "cool_pct": 0.0,
                    "neutral_pct": 0.0, "other_pct": 0.0,
                },
            },
            "vad_estimate": {
                "valence_estimate": 0.5,
                "arousal_estimate": 0.5,
                "dominance_estimate": 0.5,
            },
            "stroke_metrics": {
                "edge_density_pct": 0.0,
                "mean_edge_intensity": 0.0,
                "stroke_continuity": 0.0,
                "fragmentation_ratio": 0.0,
                "spatial_distribution": {
                    "top_left_pct": 0.0, "top_right_pct": 0.0,
                    "bottom_left_pct": 0.0, "bottom_right_pct": 0.0,
                },
            },
            "compactness": 0.0,
            "dominant_color": "unknown",
            "area_pct_of_canvas": blob.area_pct,
        }

    color_dist = compute_color_distribution(image, mask=mask)
    histogram = compute_color_histogram(image, mask=mask)
    vad_result = compute_vad_from_histogram(histogram, image)

    canny_full = apply_canny_edge_detection(image)
    canny_masked = cv2.bitwise_and(canny_full, canny_full, mask=mask)
    stroke_result = compute_stroke_metrics(canny_masked)

    compactness = _compute_compactness(mask, blob.polygon)
    dominant_color = _find_dominant_color_in_region(image, mask)

    h, w = image.shape[:2]
    area_pct = float(cv2.countNonZero(mask)) / (h * w)

    return {
        "color_distribution": color_dist,
        "vad_estimate": vad_result,
        "stroke_metrics": stroke_result,
        "compactness": compactness,
        "dominant_color": dominant_color,
        "area_pct_of_canvas": round(area_pct, 4),
    }
