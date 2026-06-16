import numpy as np
import cv2
from app.core.pdi.segmentation import (
    compute_color_distribution,
    compute_color_histogram,
    compute_vad_from_histogram,
    compute_chromatic_mass,
    compute_canvas_utilization,
    compute_visual_complexity,
    compute_lr_symmetry,
    compute_visual_entropy,
    compute_fractal_dimension,
    segment_color_hsv,
    auto_white_balance,
    _compute_content_mask,
    COLOR_RANGES_HSV,
)


def test_distribution_has_required_keys():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_color_distribution(img)
    assert "specific" in result
    assert "therapeutic_groups" in result


def test_specific_sums_approx_one():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_color_distribution(img)
    total = sum(result["specific"].values())
    assert abs(total - 1.0) < 0.02


def test_therapeutic_groups_sums_approx_one():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_color_distribution(img)
    total = sum(result["therapeutic_groups"].values())
    assert abs(total - 1.0) < 0.02


def test_red_image_warm_high():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :, 2] = 200
    img[:, :, 1] = 30
    img[:, :, 0] = 30
    result = compute_color_distribution(img)
    assert result["therapeutic_groups"]["warm_pct"] > 0.5


def test_blue_image_cool_high():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :, 0] = 200
    result = compute_color_distribution(img)
    assert result["therapeutic_groups"]["cool_pct"] > 0.5


def test_histogram_correct_lengths():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_color_histogram(img)
    assert len(result["hue"]) == 180
    assert len(result["saturation"]) == 256
    assert len(result["value"]) == 256


def test_earth_color_classified():
    hsv_img = np.zeros((50, 50, 3), dtype=np.uint8)
    hsv_img[:, :, 0] = 18
    hsv_img[:, :, 1] = 36
    hsv_img[:, :, 2] = 90
    bgr_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    result = compute_color_distribution(bgr_img)
    assert result["specific"]["earth_pct"] > 0.1


def test_blue_celeste_not_white():
    hsv_img = np.zeros((50, 50, 3), dtype=np.uint8)
    hsv_img[:, :, 0] = 105
    hsv_img[:, :, 1] = 40
    hsv_img[:, :, 2] = 200
    bgr_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    result = compute_color_distribution(bgr_img)
    assert result["specific"]["blue_pct"] > 0.3
    assert result["specific"]["white_pct"] < 0.2


def test_dark_green_not_black():
    hsv_img = np.zeros((50, 50, 3), dtype=np.uint8)
    hsv_img[:, :, 0] = 60
    hsv_img[:, :, 1] = 80
    hsv_img[:, :, 2] = 35
    bgr_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    result = compute_color_distribution(bgr_img)
    assert result["specific"]["green_pct"] > result["specific"]["black_pct"]


def test_white_background_excluded():
    content = np.zeros((30, 30, 3), dtype=np.uint8)
    content[:, :, 0] = 200
    content[:, :, 1] = 50
    content[:, :, 2] = 50
    bgr_red = cv2.cvtColor(
        np.array([[[0, 100, 255]]], dtype=np.uint8), cv2.COLOR_HSV2BGR
    )
    content[:, :] = bgr_red[0, 0]
    background = np.full((70, 100, 3), 250, dtype=np.uint8)
    background[:30, :30] = content
    result = compute_color_distribution(background)
    assert result["specific"]["red_pct"] > 0.1


def test_content_mask_excludes_white_background():
    bg = np.full((100, 100, 3), 245, dtype=np.uint8)
    bg[40:60, 40:60] = [50, 50, 200]
    mask = _compute_content_mask(bg)
    total_content = cv2.countNonZero(mask)
    total_pixels = 100 * 100
    content_ratio = total_content / total_pixels
    assert content_ratio < 0.1


def test_auto_white_balance():
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    img[:, :, 0] = 100
    img[:, :, 1] = 150
    img[:, :, 2] = 200
    balanced = auto_white_balance(img)
    assert balanced.dtype == np.uint8
    b_avg = float(np.mean(balanced[:, :, 0]))
    g_avg = float(np.mean(balanced[:, :, 1]))
    r_avg = float(np.mean(balanced[:, :, 2]))
    avg = (b_avg + g_avg + r_avg) / 3.0
    assert abs(b_avg - avg) < 1.0
    assert abs(g_avg - avg) < 1.0
    assert abs(r_avg - avg) < 1.0


def test_distribution_with_explicit_mask():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20:80, 20:80] = 255
    result = compute_color_distribution(img, mask=mask)
    assert "specific" in result
    assert "therapeutic_groups" in result
    total = sum(result["specific"].values())
    assert abs(total - 1.0) < 0.02


def test_distribution_empty_mask_returns_zeros():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    result = compute_color_distribution(img, mask=mask)
    assert result["specific"]["red_pct"] == 0.0
    assert result["therapeutic_groups"]["warm_pct"] == 0.0


def test_priority_no_double_counting():
    hsv_img = np.zeros((100, 100, 3), dtype=np.uint8)
    hsv_img[:, :, 0] = 10
    hsv_img[:, :, 1] = 120
    hsv_img[:, :, 2] = 150
    bgr_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
    result = compute_color_distribution(bgr_img)
    orange_earth_sum = result["specific"]["orange_pct"] + result["specific"]["earth_pct"]
    assert orange_earth_sum <= 1.01


def test_specific_keys_include_earth():
    img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    result = compute_color_distribution(img)
    assert "earth_pct" in result["specific"]


def test_canvas_utilization():
    img = np.full((100, 100, 3), 245, dtype=np.uint8)
    img[40:60, 40:60] = 0
    result = compute_canvas_utilization(img)
    assert 0.0 <= result["total_used_pct"] <= 1.0
    assert result["expansion_flag"] in ("micropsia", "normal", "expansion")


def test_lr_symmetry():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = compute_lr_symmetry(img)
    assert 0.0 <= result <= 1.0


def test_visual_entropy():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_visual_entropy(img)
    assert result > 0


def test_fractal_dimension():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_fractal_dimension(img)
    assert result >= 0.0


def test_visual_complexity():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_visual_complexity(img)
    assert "fractal_dimension" in result
    assert "image_entropy" in result
    assert "organization_level" in result


def test_vad_from_histogram_with_image():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :, 0] = 200
    img[:, :, 1] = 50
    img[:, :, 2] = 50
    result = compute_vad_from_histogram({}, img)
    assert "valence_estimate" in result
    assert "arousal_estimate" in result
    assert "dominance_estimate" in result


def test_chromatic_mass():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[30:70, 30:70] = [50, 50, 200]
    result = compute_chromatic_mass(img)
    assert "dominant_group" in result
    assert "centroid" in result
    assert "quadrant_distribution" in result