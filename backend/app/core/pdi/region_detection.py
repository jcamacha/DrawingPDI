import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

from app.core.pdi.segmentation import COLOR_RANGES_HSV
from app.core.pdi.spatial_analysis import classify_spatial_zone


@dataclass
class BlobRegion:
    color_name: str
    mask: np.ndarray
    bbox: Tuple[int, int, int, int]
    polygon: np.ndarray
    centroid: Tuple[float, float]
    area_pct: float
    semiotic_zone: str = ""
    region_id: str = ""


def _mask_to_polygon(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.array([])
    largest = max(contours, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(largest, True)
    return cv2.approxPolyDP(largest, epsilon, True)


def _mask_to_bbox(mask: np.ndarray) -> Tuple[int, int, int, int]:
    coords = cv2.findNonZero(mask)
    if coords is None:
        return (0, 0, 0, 0)
    return cv2.boundingRect(coords)


def _compute_centroid(mask: np.ndarray) -> Tuple[float, float]:
    M = cv2.moments(mask)
    if M["m00"] == 0:
        h, w = mask.shape[:2]
        return (w / 2.0, h / 2.0)
    cx = M["m10"] / M["m00"]
    cy = M["m01"] / M["m00"]
    return (cx, cy)


def detect_color_blobs(
    image: np.ndarray,
    min_area_pct: float = 0.005,
    max_regions: int = 30,
) -> List[BlobRegion]:
    h, w = image.shape[:2]
    total_pixels = h * w
    min_area = int(total_pixels * min_area_pct)

    regions: List[BlobRegion] = []
    region_counter = 0

    for color_name, (lower, upper) in COLOR_RANGES_HSV.items():
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        if cv2.countNonZero(mask) < min_area:
            continue

        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
            mask, connectivity=8
        )

        for label_idx in range(1, num_labels):
            area = stats[label_idx, cv2.CC_STAT_AREA]
            if area < min_area:
                continue

            blob_mask = (labels == label_idx).astype(np.uint8) * 255
            bbox = _mask_to_bbox(blob_mask)
            polygon = _mask_to_polygon(blob_mask)
            centroid = _compute_centroid(blob_mask)
            area_pct = area / total_pixels

            x_norm = centroid[0] / w
            y_norm = centroid[1] / h
            zone = classify_spatial_zone(x_norm, y_norm)

            region_counter += 1
            regions.append(BlobRegion(
                color_name=color_name,
                mask=blob_mask,
                bbox=bbox,
                polygon=polygon,
                centroid=centroid,
                area_pct=round(area_pct, 4),
                semiotic_zone=zone,
                region_id=f"reg_{region_counter:03d}",
            ))

            if len(regions) >= max_regions:
                return regions

    regions.sort(key=lambda r: r.area_pct, reverse=True)
    return regions[:max_regions]
