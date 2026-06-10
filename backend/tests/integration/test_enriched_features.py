import time
import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from app.main import app

TEST_IMAGE = Path("tests/fixtures/sample_800x600.jpg")


@pytest.mark.asyncio
async def test_enriched_features_returned():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(TEST_IMAGE, "rb") as f:
            r = await client.post(
                "/api/v1/images/upload",
                files={"file": ("sample.jpg", f, "image/jpeg")},
            )
        assert r.status_code == 200
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.post(f"/api/v1/images/{analysis_id}/analyze")
        assert r.status_code == 200
        data = r.json()["data"]

        assert "enriched_features" in data
        ef = data["enriched_features"]
        assert "computational_vad" in ef
        assert "semiotic_mass" in ef

        vad = ef["computational_vad"]
        assert 0.0 <= vad["valence_estimate"] <= 1.0
        assert 0.0 <= vad["arousal_estimate"] <= 1.0
        assert 0.0 <= vad["dominance_estimate"] <= 1.0

        sm = ef["semiotic_mass"]
        assert "dominant_group" in sm
        assert sm["dominant_group"] in ("warm", "cool", "neutral")
        assert "predominant_color_centroid" in sm
        assert 0.0 <= sm["predominant_color_centroid"]["x_norm"] <= 1.0
        assert 0.0 <= sm["predominant_color_centroid"]["y_norm"] <= 1.0


@pytest.mark.asyncio
async def test_stroke_metrics_extended_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(TEST_IMAGE, "rb") as f:
            r = await client.post(
                "/api/v1/images/upload",
                files={"file": ("sample.jpg", f, "image/jpeg")},
            )
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.post(f"/api/v1/images/{analysis_id}/analyze")
        data = r.json()["data"]

        sm = data["stroke_metrics"]
        assert "fragmentation_ratio" in sm
        assert 0.0 <= sm["fragmentation_ratio"] <= 1.0
        assert "spatial_distribution" in sm
        sd = sm["spatial_distribution"]
        total = sd["top_left_pct"] + sd["top_right_pct"] + sd["bottom_left_pct"] + sd["bottom_right_pct"]
        assert abs(total - 1.0) < 0.02 or total < 0.01


@pytest.mark.asyncio
async def test_detected_symbols_empty_list():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(TEST_IMAGE, "rb") as f:
            r = await client.post(
                "/api/v1/images/upload",
                files={"file": ("sample.jpg", f, "image/jpeg")},
            )
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.post(f"/api/v1/images/{analysis_id}/analyze")
        data = r.json()["data"]
        assert "detected_symbols" in data
        assert data["detected_symbols"] == []


@pytest.mark.asyncio
async def test_semiotic_mass_quadrant_sums_approx_one():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(TEST_IMAGE, "rb") as f:
            r = await client.post(
                "/api/v1/images/upload",
                files={"file": ("sample.jpg", f, "image/jpeg")},
            )
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.post(f"/api/v1/images/{analysis_id}/analyze")
        data = r.json()["data"]

        qmd = data["enriched_features"]["semiotic_mass"]["quadrant_mass_distribution"]
        total = qmd["top_left_pct"] + qmd["top_right_pct"] + qmd["bottom_left_pct"] + qmd["bottom_right_pct"]
        assert abs(total - 1.0) < 0.02