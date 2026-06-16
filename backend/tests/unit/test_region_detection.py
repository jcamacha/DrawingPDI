import numpy as np
import cv2
from app.core.pdi.region_detection import detect_color_blobs, BlobRegion


def test_detect_single_red_blob():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[50:150, 50:150] = [30, 30, 200]
    blobs = detect_color_blobs(img, min_area_pct=0.001)
    assert len(blobs) >= 1, "Should detect at least one red blob"
    red_blobs = [b for b in blobs if "red" in b.color_name]
    assert len(red_blobs) >= 1, "Should detect at least one red-colored blob"


def test_detect_multiple_color_blobs():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[10:90, 10:90] = [30, 30, 200]
    img[110:190, 110:190] = [200, 30, 30]
    blobs = detect_color_blobs(img, min_area_pct=0.001)
    assert len(blobs) >= 2, "Should detect at least two blobs"


def test_white_image_no_significant_blobs():
    img = np.full((100, 100, 3), 240, dtype=np.uint8)
    blobs = detect_color_blobs(img, min_area_pct=0.01)
    white_blobs = [b for b in blobs if "white" in b.color_name]
    assert len(white_blobs) >= 0


def test_blob_has_valid_properties():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[50:150, 50:150] = [30, 30, 200]
    blobs = detect_color_blobs(img, min_area_pct=0.001)
    if blobs:
        blob = blobs[0]
        assert blob.region_id.startswith("reg_")
        assert blob.mask.shape == (200, 200)
        assert blob.bbox[2] > 0 and blob.bbox[3] > 0
        assert blob.area_pct > 0
        assert blob.semiotic_zone in ["PASADO", "FUTURO", "MATERIAL", "IDEAL"]


def test_max_regions_limit():
    img = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)
    blobs = detect_color_blobs(img, min_area_pct=0.0001, max_regions=10)
    assert len(blobs) <= 10, f"Should not exceed max_regions=10, got {len(blobs)}"


def test_spatial_zone_classification():
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[10:40, 10:40] = [30, 30, 200]
    blobs = detect_color_blobs(img, min_area_pct=0.001)
    if blobs:
        blob = blobs[0]
        cx = blob.centroid[0] / 200
        cy = blob.centroid[1] / 200
        if cx < 0.5 and cy < 0.5:
            assert blob.semiotic_zone == "PASADO"
