import numpy as np
import cv2
from app.core.pdi.segmentation import (
    compute_vad_from_histogram,
    compute_chromatic_mass,
    compute_color_distribution,
    compute_color_histogram,
)


def test_vad_red_image_high_valence_arousal():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :, 2] = 200
    img[:, :, 1] = 30
    img[:, :, 0] = 30
    vad = compute_vad_from_histogram({}, image=img)
    assert vad["valence_estimate"] > 0.5, f"Red image valence should be > 0.5, got {vad['valence_estimate']}"
    assert vad["arousal_estimate"] > 0.5, f"Red image arousal should be > 0.5, got {vad['arousal_estimate']}"


def test_vad_blue_image_low_valence():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:, :, 0] = 200
    vad = compute_vad_from_histogram({}, image=img)
    assert vad["valence_estimate"] < 0.5, f"Blue image valence should be < 0.5, got {vad['valence_estimate']}"


def test_vad_values_in_range():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    vad = compute_vad_from_histogram({}, image=img)
    for key in ["valence_estimate", "arousal_estimate", "dominance_estimate"]:
        assert 0.0 <= vad[key] <= 1.0, f"{key} out of range: {vad[key]}"


def test_mass_red_block_top_left_centroid():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[:, :, 0] = 30
    img[:, :, 1] = 30
    img[:, :, 2] = 200
    result = compute_chromatic_mass(img)
    assert result["dominant_group"] == "warm", f"Dominant group should be 'warm', got '{result['dominant_group']}'"
    centroid = result["centroid"]
    assert centroid["x_norm"] < 0.6 and centroid["y_norm"] < 0.6, \
        f"Centroid should be near center for uniform warm image, got ({centroid['x_norm']}, {centroid['y_norm']})"


def test_mass_white_image_dominant_neutral():
    img = np.full((100, 100, 3), 240, dtype=np.uint8)
    result = compute_chromatic_mass(img)
    assert result["dominant_group"] == "neutral", f"White image should be neutral, got {result['dominant_group']}"


def test_mass_quadrant_distribution_sums_approx_one():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    result = compute_chromatic_mass(img)
    total = sum(result["quadrant_distribution"].values())
    assert abs(total - 1.0) < 0.02, f"Quadrant distribution should sum to ~1.0, got {total}"


def test_mass_random_image_no_exception():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = compute_chromatic_mass(img)
    assert "dominant_group" in result
    assert "centroid" in result
    assert "quadrant_distribution" in result


def test_distribution_with_mask_no_regression():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result_no_mask = compute_color_distribution(img)
    result_with_none = compute_color_distribution(img, mask=None)
    assert result_no_mask["specific"]["red_pct"] == result_with_none["specific"]["red_pct"]


def test_histogram_with_mask_different():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[:50, :50] = 255
    result_no_mask = compute_color_histogram(img)
    result_with_mask = compute_color_histogram(img, mask=mask)
    assert result_with_mask["hue"] != result_no_mask["hue"]


def test_histogram_empty_mask_returns_zeros():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    result = compute_color_histogram(img, mask=mask)
    assert sum(result["hue"]) == 0
    assert sum(result["saturation"]) == 0