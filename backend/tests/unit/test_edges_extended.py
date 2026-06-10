from app.core.pdi.edges import apply_canny_edge_detection, compute_stroke_metrics
from app.core.pdi.semiotic_config import classify_semiotic_zone, SEMIOTIC_ZONES
import numpy as np
import cv2


def test_fragmentation_ratio_in_range():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    canny = apply_canny_edge_detection(img)
    metrics = compute_stroke_metrics(canny)
    assert 0.0 <= metrics["fragmentation_ratio"] <= 1.0, \
        f"fragmentation_ratio out of range: {metrics['fragmentation_ratio']}"


def test_quadrant_sum_approx_total():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    canny = apply_canny_edge_detection(img)
    metrics = compute_stroke_metrics(canny)
    q = metrics["spatial_distribution"]
    total = q["top_left_pct"] + q["top_right_pct"] + q["bottom_left_pct"] + q["bottom_right_pct"]
    assert abs(total - metrics["edge_density_pct"]) < 0.02 or abs(total - 1.0) < 0.02, \
        f"Quadrant sum {total} doesn't match edge_density_pct {metrics['edge_density_pct']}"


def test_black_image_zero_fragmentation():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    canny = apply_canny_edge_detection(img)
    metrics = compute_stroke_metrics(canny)
    assert metrics["fragmentation_ratio"] == 0.0
    sd = metrics["spatial_distribution"]
    assert sd["top_left_pct"] == 0.0
    assert sd["top_right_pct"] == 0.0
    assert sd["bottom_left_pct"] == 0.0
    assert sd["bottom_right_pct"] == 0.0


def test_pre_blur_parameter():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result_no_blur = apply_canny_edge_detection(img, pre_blur_kernel=0)
    result_with_blur = apply_canny_edge_detection(img, pre_blur_kernel=7)
    assert result_no_blur.shape == result_with_blur.shape


def test_canny_with_mask():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[:50, :50] = 255
    result = apply_canny_edge_detection(img, mask=mask)
    bottom_right_count = np.count_nonzero(result[50:, 50:])
    assert bottom_right_count == 0, "Masked area should have no edges"


def test_canny_empty_mask():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    result = apply_canny_edge_detection(img, mask=mask)
    assert np.count_nonzero(result) == 0, "Empty mask should return all zeros"


def test_existing_five_tests_still_pass():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    canny = apply_canny_edge_detection(img)
    assert canny.ndim == 2

    apply_canny_edge_detection(img)

    black = np.zeros((100, 100, 3), dtype=np.uint8)
    canny_black = apply_canny_edge_detection(black)
    metrics = compute_stroke_metrics(canny_black)
    assert metrics["edge_density_pct"] == 0.0

    metrics = compute_stroke_metrics(canny)
    assert "edge_density_pct" in metrics
    assert "mean_edge_intensity" in metrics
    assert "stroke_continuity" in metrics
    assert "fragmentation_ratio" in metrics
    assert "spatial_distribution" in metrics

    cv2_img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2_img[50:150, 50:150] = 255
    canny_edges = apply_canny_edge_detection(cv2_img)
    m = compute_stroke_metrics(canny_edges)
    assert m["edge_density_pct"] > 0


def test_semiotic_zone_past():
    assert classify_semiotic_zone(0.1, 0.1) == "PASADO"


def test_semiotic_zone_future():
    assert classify_semiotic_zone(0.9, 0.1) == "FUTURO"


def test_semiotic_zone_material():
    assert classify_semiotic_zone(0.1, 0.9) == "MATERIAL"


def test_semiotic_zone_ideal():
    assert classify_semiotic_zone(0.9, 0.9) == "IDEAL"


def test_semiotic_zones_dict_has_four_entries():
    assert len(SEMIOTIC_ZONES) == 4
    assert "PASADO" in SEMIOTIC_ZONES
    assert "FUTURO" in SEMIOTIC_ZONES
    assert "MATERIAL" in SEMIOTIC_ZONES
    assert "IDEAL" in SEMIOTIC_ZONES


def test_semiotic_zone_boundaries():
    assert classify_semiotic_zone(0.5, 0.1) == "FUTURO"
    assert classify_semiotic_zone(0.1, 0.5) == "MATERIAL"
    assert classify_semiotic_zone(0.5, 0.5) == "IDEAL"