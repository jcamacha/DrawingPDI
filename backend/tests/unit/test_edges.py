import numpy as np
from app.core.pdi.edges import apply_canny_edge_detection, compute_stroke_metrics


def test_canny_output_is_2d():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = apply_canny_edge_detection(img)
    assert result.ndim == 2


def test_canny_no_exception():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    apply_canny_edge_detection(img)


def test_black_image_zero_density():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    canny = apply_canny_edge_detection(img)
    metrics = compute_stroke_metrics(canny)
    assert metrics["edge_density_pct"] == 0.0


def test_stroke_metrics_has_three_keys():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    canny = apply_canny_edge_detection(img)
    metrics = compute_stroke_metrics(canny)
    assert "edge_density_pct" in metrics
    assert "mean_edge_intensity" in metrics
    assert "stroke_continuity" in metrics


def test_synthetic_edges_positive_density():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2_img = img.copy()
    cv2_img[50:150, 50:150] = 255
    canny = apply_canny_edge_detection(cv2_img)
    metrics = compute_stroke_metrics(canny)
    assert metrics["edge_density_pct"] > 0
