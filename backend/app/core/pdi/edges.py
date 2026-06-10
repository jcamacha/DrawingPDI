import cv2
import numpy as np


def apply_canny_edge_detection(
    image: np.ndarray,
    threshold1: float = 100.0,
    threshold2: float = 200.0,
    pre_blur_kernel: int = 7,
    mask: np.ndarray = None,
) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if pre_blur_kernel > 0:
        ksize = pre_blur_kernel if pre_blur_kernel % 2 == 1 else pre_blur_kernel + 1
        gray = cv2.GaussianBlur(gray, (ksize, ksize), 0)

    canny = cv2.Canny(gray, threshold1, threshold2)

    if mask is not None:
        if cv2.countNonZero(mask) == 0:
            return np.zeros_like(canny)
        canny = cv2.bitwise_and(canny, canny, mask=mask)

    return canny


def compute_stroke_metrics(canny_image: np.ndarray) -> dict:
    total = canny_image.shape[0] * canny_image.shape[1]
    edge_pixels = np.count_nonzero(canny_image)

    edge_density_pct = round(edge_pixels / total, 4) if total > 0 else 0.0

    nonzero_values = canny_image[canny_image > 0]
    mean_edge_intensity = float(np.mean(nonzero_values)) if len(nonzero_values) > 0 else 0.0

    contours, _ = cv2.findContours(
        canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    lengths = [cv2.arcLength(c, False) for c in contours]
    stroke_continuity = float(np.mean(lengths)) if lengths else 0.0

    short_threshold = 20.0
    short_contours = sum(1 for l in lengths if l < short_threshold)
    fragmentation_ratio = round(float(short_contours / len(contours)), 4) if contours else 0.0

    h, w = canny_image.shape[:2]
    half_h = h // 2
    half_w = w // 2

    tl = np.count_nonzero(canny_image[:half_h, :half_w])
    tr = np.count_nonzero(canny_image[:half_h, half_w:])
    bl = np.count_nonzero(canny_image[half_h:, :half_w])
    br = np.count_nonzero(canny_image[half_h:, half_w:])
    total_edges = max(float(edge_pixels), 1.0)

    spatial_distribution = {
        "top_left_pct": round(float(tl / total_edges), 4),
        "top_right_pct": round(float(tr / total_edges), 4),
        "bottom_left_pct": round(float(bl / total_edges), 4),
        "bottom_right_pct": round(float(br / total_edges), 4),
    }

    return {
        "edge_density_pct": edge_density_pct,
        "mean_edge_intensity": round(mean_edge_intensity, 2),
        "stroke_continuity": round(stroke_continuity, 2),
        "fragmentation_ratio": fragmentation_ratio,
        "spatial_distribution": spatial_distribution,
    }