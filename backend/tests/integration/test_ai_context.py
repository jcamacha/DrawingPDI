import base64
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _create_test_image_b64(width=200, height=200, color=None):
    if color is None:
        img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    else:
        img = np.full((height, width, 3), color, dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    return base64.b64encode(buffer).decode("utf-8"), img


def _upload_and_analyze(client, img_b64):
    upload_resp = client.post(
        "/api/v1/images/upload",
        files={"file": ("test.jpg", base64.b64decode(img_b64), "image/jpeg")},
    )
    assert upload_resp.status_code == 200
    analysis_id = upload_resp.json()["data"]["analysis_id"]

    analyze_resp = client.post(f"/api/v1/images/{analysis_id}/analyze")
    assert analyze_resp.status_code == 200
    return analysis_id


def test_ai_ctx_full_flow():
    img_b64, _ = _create_test_image_b64(
        color=(30, 30, 200)
    )
    analysis_id = _upload_and_analyze(client, img_b64)

    resp = client.post(f"/api/v1/images/{analysis_id}/ai-context")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "meta" in data
    assert "regions" in data["data"]
    assert "global_context" in data["data"]
    assert "interpretation_prompt_template" in data["data"]


def test_ai_ctx_session_not_found():
    resp = client.post("/api/v1/images/nonexistent-id/ai-context")
    assert resp.status_code == 404
    assert resp.json()["detail"]["code"] == "SESSION_NOT_FOUND"


def test_ai_ctx_analysis_incomplete():
    img_b64, _ = _create_test_image_b64()
    upload_resp = client.post(
        "/api/v1/images/upload",
        files={"file": ("test.jpg", base64.b64decode(img_b64), "image/jpeg")},
    )
    analysis_id = upload_resp.json()["data"]["analysis_id"]

    resp = client.post(f"/api/v1/images/{analysis_id}/ai-context")
    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "ANALYSIS_INCOMPLETE"


def test_ai_ctx_regions_have_thumbnails():
    img_b64, _ = _create_test_image_b64(
        color=(30, 30, 200)
    )
    analysis_id = _upload_and_analyze(client, img_b64)

    resp = client.post(f"/api/v1/images/{analysis_id}/ai-context")
    assert resp.status_code == 200
    regions = resp.json()["data"]["regions"]
    if len(regions) > 0:
        for region in regions:
            assert "thumbnail_b64" in region
            assert len(region["thumbnail_b64"]) > 0
            decoded = base64.b64decode(region["thumbnail_b64"])
            arr = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
            assert arr is not None
            assert arr.shape[0] == 224 and arr.shape[1] == 224


def test_ai_ctx_regions_have_spatial_quadrants():
    img_b64, _ = _create_test_image_b64(
        color=(30, 30, 200)
    )
    analysis_id = _upload_and_analyze(client, img_b64)

    resp = client.post(f"/api/v1/images/{analysis_id}/ai-context")
    assert resp.status_code == 200
    regions = resp.json()["data"]["regions"]
    valid_zones = {"PASADO", "FUTURO", "MATERIAL", "IDEAL"}
    for region in regions:
        assert region["spatial"]["spatial_quadrant"] in valid_zones
        assert len(region["spatial"]["quadrant_description"]) > 0


def test_ai_ctx_global_context_populated():
    img_b64, _ = _create_test_image_b64(
        color=(30, 30, 200)
    )
    analysis_id = _upload_and_analyze(client, img_b64)

    resp = client.post(f"/api/v1/images/{analysis_id}/ai-context")
    assert resp.status_code == 200
    gc = resp.json()["data"]["global_context"]
    assert gc["dominant_emotional_tone"] in ["warm", "cool", "neutral", "unknown"]
    assert 0.0 <= gc["overall_vad"]["valence_estimate"] <= 1.0
    assert 0.0 <= gc["overall_vad"]["arousal_estimate"] <= 1.0
    assert 0.0 <= gc["overall_vad"]["dominance_estimate"] <= 1.0
    assert gc["fragmentation_level"] in ["low", "moderate", "high", "unknown"]


def test_ai_ctx_relationships_present():
    img_b64, _ = _create_test_image_b64(
        color=(30, 30, 200)
    )
    analysis_id = _upload_and_analyze(client, img_b64)

    resp = client.post(f"/api/v1/images/{analysis_id}/ai-context")
    assert resp.status_code == 200
    regions = resp.json()["data"]["regions"]
    for region in regions:
        assert "relationships" in region
        assert "overlaps_with" in region["relationships"]
        assert "proximity_to" in region["relationships"]
        assert "layer_order" in region["relationships"]
