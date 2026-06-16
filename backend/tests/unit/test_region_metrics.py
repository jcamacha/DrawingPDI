import numpy as np
import cv2
from app.core.pdi.region_detection import detect_color_blobs
from app.core.pdi.region_metrics import compute_region_metrics


def _create_test_blob(image, mask):
    from app.core.pdi.region_detection import BlobRegion
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygon = max(contours, key=cv2.contourArea) if contours else np.array([])
    bbox = cv2.boundingRect(mask)
    M = cv2.moments(mask)
    cx = M["m10"] / M["m00"] if M["m00"] > 0 else 100
    cy = M["m01"] / M["m00"] if M["m00"] > 0 else 100
    return BlobRegion(
        color_name="red",
        mask=mask,
        bbox=bbox,
        polygon=polygon,
        centroid=(cx, cy),
        area_pct=0.1,
        semiotic_zone="PASADO",
        region_id="reg_test",
    )


def test_region_metrics_red_blob():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    mask = np.zeros((200, 200), dtype=np.uint8)
    mask[50:150, 50:150] = 255
    img[50:150, 50:150] = [30, 30, 200]
    blob = _create_test_blob(img, mask)
    metrics = compute_region_metrics(img, blob)
    assert "color_distribution" in metrics
    assert "vad_estimate" in metrics
    assert "stroke_metrics" in metrics
    assert "compactness" in metrics
    assert "dominant_color" in metrics
    assert "area_pct_of_canvas" in metrics


def test_region_metrics_dominant_color_red():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    mask = np.zeros((200, 200), dtype=np.uint8)
    mask[50:150, 50:150] = 255
    img[50:150, 50:150] = [30, 30, 200]
    blob = _create_test_blob(img, mask)
    metrics = compute_region_metrics(img, blob)
    assert metrics["dominant_color"] == "red"


def test_region_metrics_circular_blob_compactness():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    mask = np.zeros((200, 200), dtype=np.uint8)
    cv2.circle(mask, (100, 100), 50, 255, -1)
    img[mask > 0] = [30, 30, 200]
    blob = _create_test_blob(img, mask)
    metrics = compute_region_metrics(img, blob)
    assert 0.5 < metrics["compactness"] <= 1.0, f"Circular blob should have high compactness, got {metrics['compactness']}"


def test_region_metrics_empty_blob_returns_defaults():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    mask = np.zeros((100, 100), dtype=np.uint8)
    blob = _create_test_blob(img, mask)
    metrics = compute_region_metrics(img, blob)
    assert metrics["color_distribution"]["specific"]["red_pct"] == 0.0
    assert metrics["compactness"] == 0.0


def test_region_metrics_vad_in_range():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    mask = np.zeros((200, 200), dtype=np.uint8)
    mask[50:150, 50:150] = 255
    img[50:150, 50:150] = [30, 30, 200]
    blob = _create_test_blob(img, mask)
    metrics = compute_region_metrics(img, blob)
    vad = metrics["vad_estimate"]
    for key in ["valence_estimate", "arousal_estimate", "dominance_estimate"]:
        assert 0.0 <= vad[key] <= 1.0, f"{key} out of range: {vad[key]}"
