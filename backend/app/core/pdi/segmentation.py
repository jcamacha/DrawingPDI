import cv2
import numpy as np
from typing import Tuple

COLOR_RANGES_HSV = {
    "red_low": ((0, 70, 50), (10, 255, 255)),
    "red_high": ((170, 70, 50), (180, 255, 255)),
    "orange": ((8, 50, 70), (25, 255, 255)),
    "yellow": ((15, 40, 70), (40, 255, 255)),
    "green": ((35, 40, 30), (85, 255, 255)),
    "blue": ((90, 40, 40), (135, 255, 255)),
    "violet": ((130, 60, 50), (160, 255, 255)),
    "earth": ((8, 30, 40), (25, 180, 180)),
    "white": ((0, 0, 200), (180, 15, 255)),
    "black": ((0, 0, 0), (180, 255, 30)),
    "gray": ((0, 0, 31), (180, 30, 199)),
}

WARM_COLORS = ["red_low", "red_high", "orange", "yellow", "earth"]
COOL_COLORS = ["green", "blue", "violet"]
NEUTRAL_COLORS = ["white", "black", "gray"]

_WHITE_BG_THRESHOLD = 240
_MORPH_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))


def segment_color_hsv(
    image: np.ndarray,
    lower_bound: Tuple,
    upper_bound: Tuple,
) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, np.array(lower_bound), np.array(upper_bound))


def auto_white_balance(image: np.ndarray) -> np.ndarray:
    b_avg = float(np.mean(image[:, :, 0]))
    g_avg = float(np.mean(image[:, :, 1]))
    r_avg = float(np.mean(image[:, :, 2]))
    avg_gray = (b_avg + g_avg + r_avg) / 3.0
    if avg_gray < 1.0:
        return image
    scale_b = avg_gray / max(b_avg, 1.0)
    scale_g = avg_gray / max(g_avg, 1.0)
    scale_r = avg_gray / max(r_avg, 1.0)
    balanced = np.zeros_like(image, dtype=np.float64)
    balanced[:, :, 0] = image[:, :, 0] * scale_b
    balanced[:, :, 1] = image[:, :, 1] * scale_g
    balanced[:, :, 2] = image[:, :, 2] * scale_r
    return cv2.convertScaleAbs(balanced)


def _compute_content_mask(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, _WHITE_BG_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, _MORPH_KERNEL)
    return mask


def _prepare_image_and_mask(image: np.ndarray, mask: np.ndarray = None):
    if mask is not None:
        if cv2.countNonZero(mask) == 0:
            return None, None, None
        if _has_significant_background(image):
            processed = auto_white_balance(image.copy())
        else:
            processed = image.copy()
        effective_mask = mask
        masked_image = cv2.bitwise_and(processed, processed, mask=effective_mask)
        total_pixels = max(float(cv2.countNonZero(effective_mask)), 1.0)
        return processed, masked_image, effective_mask, total_pixels

    content_mask_raw = _compute_content_mask(image)
    bg_pct = 1.0 - float(cv2.countNonZero(content_mask_raw)) / float(image.shape[0] * image.shape[1])
    if bg_pct >= 0.15:
        processed = auto_white_balance(image.copy())
        effective_mask = _compute_content_mask(processed)
    else:
        processed = image.copy()
        effective_mask = content_mask_raw

    masked_image = cv2.bitwise_and(processed, processed, mask=effective_mask)
    total_pixels = max(float(cv2.countNonZero(effective_mask)), 1.0)
    return processed, masked_image, effective_mask, total_pixels


def _has_significant_background(image: np.ndarray) -> bool:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    white_pixels = float(np.count_nonzero(gray >= _WHITE_BG_THRESHOLD))
    total = float(image.shape[0] * image.shape[1])
    return (white_pixels / total) >= 0.15


_COLOR_PRIORITY = [
    "white", "black", "gray",
    "red_low", "red_high", "violet", "blue", "green",
    "yellow", "orange", "earth",
]


def compute_color_distribution(image: np.ndarray, mask: np.ndarray = None) -> dict:
    _SPECIFIC_KEYS = [
        "red_pct", "orange_pct", "yellow_pct", "green_pct", "blue_pct",
        "violet_pct", "earth_pct", "white_pct", "black_pct", "gray_pct", "other_pct",
    ]

    if mask is not None and cv2.countNonZero(mask) == 0:
        return {
            "specific": {k: 0.0 for k in _SPECIFIC_KEYS},
            "therapeutic_groups": {"warm_pct": 0.0, "cool_pct": 0.0, "neutral_pct": 0.0, "other_pct": 0.0},
        }

    if mask is not None:
        if _has_significant_background(image):
            processed = auto_white_balance(image.copy())
        else:
            processed = image.copy()
        effective_mask = mask
        masked_image = cv2.bitwise_and(processed, processed, mask=effective_mask)
        total_pixels = max(float(cv2.countNonZero(effective_mask)), 1.0)
    else:
        content_mask_raw = _compute_content_mask(image)
        bg_pct = 1.0 - float(cv2.countNonZero(content_mask_raw)) / float(image.shape[0] * image.shape[1])
        if bg_pct >= 0.15:
            processed = auto_white_balance(image.copy())
            effective_mask = _compute_content_mask(processed)
        else:
            processed = image.copy()
            effective_mask = content_mask_raw
        masked_image = cv2.bitwise_and(processed, processed, mask=effective_mask)
        total_pixels = max(float(cv2.countNonZero(effective_mask)), 1.0)

    claimed = np.zeros(image.shape[:2], dtype=np.uint8)
    color_masks = {}
    for color_name in _COLOR_PRIORITY:
        lower, upper = COLOR_RANGES_HSV[color_name]
        raw_mask = segment_color_hsv(masked_image, lower, upper)
        raw_mask = cv2.bitwise_and(raw_mask, raw_mask, mask=effective_mask)
        exclusive_mask = cv2.bitwise_and(raw_mask, raw_mask, mask=255 - claimed)
        color_masks[color_name] = exclusive_mask
        claimed = cv2.bitwise_or(claimed, exclusive_mask)

    red_mask = color_masks["red_low"] | color_masks["red_high"]
    red_pct = round(float(cv2.countNonZero(red_mask)) / total_pixels, 4)

    specific = {
        "red_pct": red_pct,
        "orange_pct": round(float(cv2.countNonZero(color_masks["orange"])) / total_pixels, 4),
        "yellow_pct": round(float(cv2.countNonZero(color_masks["yellow"])) / total_pixels, 4),
        "green_pct": round(float(cv2.countNonZero(color_masks["green"])) / total_pixels, 4),
        "blue_pct": round(float(cv2.countNonZero(color_masks["blue"])) / total_pixels, 4),
        "violet_pct": round(float(cv2.countNonZero(color_masks["violet"])) / total_pixels, 4),
        "earth_pct": round(float(cv2.countNonZero(color_masks["earth"])) / total_pixels, 4),
        "white_pct": round(float(cv2.countNonZero(color_masks["white"])) / total_pixels, 4),
        "black_pct": round(float(cv2.countNonZero(color_masks["black"])) / total_pixels, 4),
        "gray_pct": round(float(cv2.countNonZero(color_masks["gray"])) / total_pixels, 4),
    }
    accounted = sum(specific.values())
    specific["other_pct"] = round(max(0.0, 1.0 - accounted), 4)

    warm = red_pct + specific["orange_pct"] + specific["yellow_pct"] + specific["earth_pct"]
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

    if mask is not None:
        if _has_significant_background(image):
            processed = auto_white_balance(image.copy())
        else:
            processed = image.copy()
        effective_mask = mask
    else:
        content_mask_raw = _compute_content_mask(image)
        bg_pct = 1.0 - float(cv2.countNonZero(content_mask_raw)) / float(image.shape[0] * image.shape[1])
        if bg_pct >= 0.15:
            processed = auto_white_balance(image.copy())
            effective_mask = _compute_content_mask(processed)
        else:
            processed = image.copy()
            effective_mask = content_mask_raw

    hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
    hist_h = (
        cv2.calcHist([hsv], [0], effective_mask, [180], [0, 180])
        .flatten()
        .astype(int)
        .tolist()
    )
    hist_s = (
        cv2.calcHist([hsv], [1], effective_mask, [256], [0, 256])
        .flatten()
        .astype(int)
        .tolist()
    )
    hist_v = (
        cv2.calcHist([hsv], [2], effective_mask, [256], [0, 256])
        .flatten()
        .astype(int)
        .tolist()
    )
    return {"hue": hist_h, "saturation": hist_s, "value": hist_v}


def generate_hsv_mask_visualization(image: np.ndarray) -> np.ndarray:
    if _has_significant_background(image):
        processed = auto_white_balance(image.copy())
    else:
        processed = image.copy()
    mask_viz = np.zeros_like(image)
    for color_key in WARM_COLORS:
        lower, upper = COLOR_RANGES_HSV[color_key]
        m = segment_color_hsv(processed, lower, upper)
        mask_viz[m > 0] = [0, 0, 200]
    for color_key in COOL_COLORS:
        lower, upper = COLOR_RANGES_HSV[color_key]
        m = segment_color_hsv(processed, lower, upper)
        mask_viz[m > 0] = [200, 0, 0]
    for color_key in NEUTRAL_COLORS:
        lower, upper = COLOR_RANGES_HSV[color_key]
        m = segment_color_hsv(processed, lower, upper)
        mask_viz[m > 0] = [150, 150, 150]
    return mask_viz


VAD_COLOR_WEIGHTS = {
    "red":      {"valence": 0.85, "arousal": 0.80, "dominance": 0.70},
    "orange":   {"valence": 0.70, "arousal": 0.65, "dominance": 0.50},
    "yellow":   {"valence": 0.80, "arousal": 0.55, "dominance": 0.40},
    "green":    {"valence": 0.50, "arousal": 0.30, "dominance": 0.40},
    "blue":     {"valence": 0.30, "arousal": 0.25, "dominance": 0.55},
    "violet":   {"valence": 0.40, "arousal": 0.45, "dominance": 0.60},
    "earth":    {"valence": 0.40, "arousal": 0.35, "dominance": 0.50},
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
    "earth_pct": "earth",
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

    processed = auto_white_balance(image.copy()) if _has_significant_background(image) else image.copy()
    content_mask = _compute_content_mask(processed)

    combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for color_key in color_keys:
        lower, upper = COLOR_RANGES_HSV[color_key]
        mask = segment_color_hsv(processed, lower, upper)
        mask = cv2.bitwise_and(mask, mask, mask=content_mask)
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


def compute_canvas_utilization(image: np.ndarray) -> dict:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, non_white = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    total_pixels = image.shape[0] * image.shape[1]
    used_pixels = float(cv2.countNonZero(non_white))
    used_pct = round(used_pixels / max(total_pixels, 1), 4)

    if used_pct < 0.15:
        expansion_flag = "micropsia"
    elif used_pct > 0.90:
        expansion_flag = "expansion"
    else:
        expansion_flag = "normal"

    h, w = image.shape[:2]
    left_half = non_white[:, : w // 2]
    right_half = non_white[:, w // 2 :]
    left_mass = float(cv2.countNonZero(left_half))
    right_mass = float(cv2.countNonZero(right_half))
    total_mass = max(left_mass + right_mass, 1.0)
    symmetry_index = round(1.0 - abs(left_mass - right_mass) / total_mass, 4)

    return {
        "total_used_pct": used_pct,
        "expansion_flag": expansion_flag,
        "symmetry_index": symmetry_index,
    }


def compute_lr_symmetry(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    h, w = bin_img.shape[:2]
    left_half = bin_img[:, : w // 2]
    right_half = bin_img[:, w // 2 :]
    left_mass = float(cv2.countNonZero(left_half))
    right_mass = float(cv2.countNonZero(right_half))
    total_mass = max(left_mass + right_mass, 1.0)
    return round(1.0 - abs(left_mass - right_mass) / total_mass, 4)


def compute_visual_entropy(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    entropy = -float(np.sum(hist * np.log2(hist)))
    return round(entropy, 4)


def compute_fractal_dimension(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    sizes = [2, 4, 8, 16, 32, 64, 128]
    counts = []
    for size in sizes:
        h_boxes = edges.shape[0] // size
        w_boxes = edges.shape[1] // size
        count = 0
        for i in range(h_boxes):
            for j in range(w_boxes):
                if np.any(edges[i * size:(i + 1) * size, j * size:(j + 1) * size]):
                    count += 1
        counts.append(count)
    if any(c == 0 for c in counts):
        return 0.0
    log_sizes = np.log(1.0 / np.array(sizes, dtype=float))
    log_counts = np.log(np.array(counts, dtype=float))
    coeffs = np.polyfit(log_sizes, log_counts, 1)
    return round(float(coeffs[0]), 4)


def compute_visual_complexity(image: np.ndarray) -> dict:
    entropy = compute_visual_entropy(image)
    fractal_dim = compute_fractal_dimension(image)

    if entropy < 3.0:
        organization_level = "low"
    elif entropy < 5.5:
        organization_level = "moderate"
    else:
        organization_level = "high"

    return {
        "fractal_dimension": fractal_dim,
        "image_entropy": entropy,
        "organization_level": organization_level,
    }