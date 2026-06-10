import cv2
import numpy as np
from typing import Tuple

COLOR_RANGES_HSV = {
    "red_low": ((0, 70, 50), (10, 255, 255)),
    "red_high": ((170, 70, 50), (180, 255, 255)),
    "orange": ((10, 100, 100), (20, 255, 255)),
    "yellow": ((20, 100, 100), (35, 255, 255)),
    "green": ((40, 70, 50), (80, 255, 255)),
    "blue": ((100, 100, 50), (130, 255, 255)),
    "violet": ((130, 60, 50), (160, 255, 255)),
    "white": ((0, 0, 200), (180, 30, 255)),
    "black": ((0, 0, 0), (180, 255, 50)),
    "gray": ((0, 0, 50), (180, 30, 200)),
}

WARM_COLORS = ["red_low", "red_high", "orange", "yellow"]
COOL_COLORS = ["green", "blue", "violet"]
NEUTRAL_COLORS = ["white", "black", "gray"]


def segment_color_hsv(
    image: np.ndarray,
    lower_bound: Tuple,
    upper_bound: Tuple,
) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))


def compute_color_distribution(image: np.ndarray, mask: np.ndarray = None) -> dict:
    if mask is not None and cv2.countNonZero(mask) == 0:
        return {
            "specific": {k: 0.0 for k in ["red_pct","orange_pct","yellow_pct","green_pct","blue_pct","violet_pct","white_pct","black_pct","gray_pct","other_pct"]},
            "therapeutic_groups": {"warm_pct": 0.0, "cool_pct": 0.0, "neutral_pct": 0.0, "other_pct": 0.0},
        }

    if mask is not None:
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        total_pixels = max(float(np.count_nonzero(mask)), 1.0)
    else:
        masked_image = image
        total_pixels = float(image.shape[0] * image.shape[1])

    color_masks = {}
    for color, (lower, upper) in COLOR_RANGES_HSV.items():
        color_mask = segment_color_hsv(masked_image, lower, upper)
        if mask is not None:
            color_mask = cv2.bitwise_and(color_mask, color_mask, mask=mask)
        color_masks[color] = color_mask

    red_mask = color_masks["red_low"] | color_masks["red_high"]
    red_pct = round(float(np.count_nonzero(red_mask)) / total_pixels, 4)

    specific = {
        "red_pct": red_pct,
        "orange_pct": round(float(np.count_nonzero(color_masks["orange"])) / total_pixels, 4),
        "yellow_pct": round(float(np.count_nonzero(color_masks["yellow"])) / total_pixels, 4),
        "green_pct": round(float(np.count_nonzero(color_masks["green"])) / total_pixels, 4),
        "blue_pct": round(float(np.count_nonzero(color_masks["blue"])) / total_pixels, 4),
        "violet_pct": round(float(np.count_nonzero(color_masks["violet"])) / total_pixels, 4),
        "white_pct": round(float(np.count_nonzero(color_masks["white"])) / total_pixels, 4),
        "black_pct": round(float(np.count_nonzero(color_masks["black"])) / total_pixels, 4),
        "gray_pct": round(float(np.count_nonzero(color_masks["gray"])) / total_pixels, 4),
    }
    accounted = sum(specific.values())
    specific["other_pct"] = round(max(0.0, 1.0 - accounted), 4)

    warm = red_pct + specific["orange_pct"] + specific["yellow_pct"]
    cool = specific["green_pct"] + specific["blue_pct"] + specific["violet_pct"]
    neutral = specific["white_pct"] + specific["black_pct"] + specific["gray_pct"]

    therapeutic_groups = {
        "warm_pct": round(warm, 4),
        "cool_pct": round(cool, 4),
        "neutral_pct": round(neutral, 4),
        "other_pct": round(max(0.0, 1.0 - warm - cool - neutral), 4),
    }

    return {"specific": specific, "therapeutic_groups": therapeutic_groups}


def compute_color_histogram(image: np.ndarray, mask: np.ndarray = None) -> dict:
    if mask is not None and cv2.countNonZero(mask) == 0:
        return {"hue": [0] * 180, "saturation": [0] * 256, "value": [0] * 256}

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask_param = mask if mask is not None else None
    hist_h = (
        cv2.calcHist([hsv], [0], mask_param, [180], [0, 180])
        .flatten()
        .astype(int)
        .tolist()
    )
    hist_s = (
        cv2.calcHist([hsv], [1], mask_param, [256], [0, 256])
        .flatten()
        .astype(int)
        .tolist()
    )
    hist_v = (
        cv2.calcHist([hsv], [2], mask_param, [256], [0, 256])
        .flatten()
        .astype(int)
        .tolist()
    )
    return {"hue": hist_h, "saturation": hist_s, "value": hist_v}


def generate_hsv_mask_visualization(image: np.ndarray) -> np.ndarray:
    mask_viz = np.zeros_like(image)
    for color_key in WARM_COLORS:
        lower, upper = COLOR_RANGES_HSV[color_key]
        m = segment_color_hsv(image, lower, upper)
        mask_viz[m > 0] = [0, 0, 200]
    for color_key in COOL_COLORS:
        lower, upper = COLOR_RANGES_HSV[color_key]
        m = segment_color_hsv(image, lower, upper)
        mask_viz[m > 0] = [200, 0, 0]
    for color_key in NEUTRAL_COLORS:
        lower, upper = COLOR_RANGES_HSV[color_key]
        m = segment_color_hsv(image, lower, upper)
        mask_viz[m > 0] = [150, 150, 150]
    return mask_viz


VAD_COLOR_WEIGHTS = {
    "red":      {"valence": 0.85, "arousal": 0.80, "dominance": 0.70},
    "orange":   {"valence": 0.70, "arousal": 0.65, "dominance": 0.50},
    "yellow":   {"valence": 0.80, "arousal": 0.55, "dominance": 0.40},
    "green":    {"valence": 0.50, "arousal": 0.30, "dominance": 0.40},
    "blue":     {"valence": 0.30, "arousal": 0.25, "dominance": 0.55},
    "violet":   {"valence": 0.40, "arousal": 0.45, "dominance": 0.60},
    "white":    {"valence": 0.55, "arousal": 0.15, "dominance": 0.20},
    "black":    {"valence": 0.20, "arousal": 0.15, "dominance": 0.80},
    "gray":     {"valence": 0.35, "arousal": 0.10, "dominance": 0.30},
}

_VAD_SPECIFIC_KEY_MAP = {
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


def compute_vad_from_histogram(histogram: dict, image: np.ndarray = None) -> dict:
    if image is not None:
        dist = compute_color_distribution(image)
    else:
        image_from_hist = _reconstruct_image_from_histogram(histogram)
        if image_from_hist is not None:
            dist = compute_color_distribution(image_from_hist)
        else:
            return {
                "valence_estimate": 0.5,
                "arousal_estimate": 0.5,
                "dominance_estimate": 0.5,
            }

    valence_sum = 0.0
    arousal_sum = 0.0
    dominance_sum = 0.0
    weight_total = 0.0

    for specific_key, vad_key in _VAD_SPECIFIC_KEY_MAP.items():
        pct = dist["specific"].get(specific_key, 0.0)
        weights = VAD_COLOR_WEIGHTS.get(vad_key)
        if weights is None:
            continue
        valence_sum += pct * weights["valence"]
        arousal_sum += pct * weights["arousal"]
        dominance_sum += pct * weights["dominance"]
        weight_total += pct

    if weight_total > 0:
        valence_estimate = valence_sum / weight_total
        arousal_estimate = arousal_sum / weight_total
        dominance_estimate = dominance_sum / weight_total
    else:
        valence_estimate = 0.5
        arousal_estimate = 0.5
        dominance_estimate = 0.5

    return {
        "valence_estimate": round(float(np.clip(valence_estimate, 0.0, 1.0)), 4),
        "arousal_estimate": round(float(np.clip(arousal_estimate, 0.0, 1.0)), 4),
        "dominance_estimate": round(float(np.clip(dominance_estimate, 0.0, 1.0)), 4),
    }


def _reconstruct_image_from_histogram(histogram: dict):
    try:
        from app.core.pdi.session import _sessions
        return None
    except Exception:
        return None


def compute_chromatic_mass(image: np.ndarray) -> dict:
    dist = compute_color_distribution(image)
    therapeutic_groups = dist["therapeutic_groups"]

    group_pcts = {
        "warm": therapeutic_groups["warm_pct"],
        "cool": therapeutic_groups["cool_pct"],
        "neutral": therapeutic_groups["neutral_pct"],
    }
    dominant_group = max(group_pcts, key=lambda k: group_pcts[k])
    if group_pcts["warm"] == group_pcts["cool"] and group_pcts["warm"] >= group_pcts["neutral"]:
        dominant_group = "warm"
    elif group_pcts["warm"] == group_pcts["neutral"] and group_pcts["warm"] >= group_pcts["cool"]:
        dominant_group = "warm"

    dominant_color_keys = {
        "warm": WARM_COLORS,
        "cool": COOL_COLORS,
        "neutral": NEUTRAL_COLORS,
    }
    color_keys = dominant_color_keys[dominant_group]

    combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for color_key in color_keys:
        lower, upper = COLOR_RANGES_HSV[color_key]
        mask = segment_color_hsv(image, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, mask)

    M = cv2.moments(combined_mask)
    if M["m00"] == 0:
        centroid = {"x_norm": 0.5, "y_norm": 0.5}
    else:
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        h, w = image.shape[:2]
        centroid = {
            "x_norm": round(float(cx / w), 4),
            "y_norm": round(float(cy / h), 4),
        }

    h, w = combined_mask.shape[:2]
    half_h = h // 2
    half_w = w // 2
    total_mask_pixels = max(float(np.count_nonzero(combined_mask)), 1.0)

    top_left = np.count_nonzero(combined_mask[:half_h, :half_w])
    top_right = np.count_nonzero(combined_mask[:half_h, half_w:])
    bottom_left = np.count_nonzero(combined_mask[half_h:, :half_w])
    bottom_right = np.count_nonzero(combined_mask[half_h:, half_w:])

    quadrant_distribution = {
        "top_left_pct": round(float(top_left / total_mask_pixels), 4),
        "top_right_pct": round(float(top_right / total_mask_pixels), 4),
        "bottom_left_pct": round(float(bottom_left / total_mask_pixels), 4),
        "bottom_right_pct": round(float(bottom_right / total_mask_pixels), 4),
    }

    return {
        "dominant_group": dominant_group,
        "centroid": centroid,
        "quadrant_distribution": quadrant_distribution,
    }
