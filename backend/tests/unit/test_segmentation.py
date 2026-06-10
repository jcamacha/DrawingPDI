import numpy as np
from app.core.pdi.segmentation import (
    compute_color_distribution,
    compute_color_histogram,
    segment_color_hsv,
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
