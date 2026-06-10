import time
import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from app.main import app

TEST_IMAGE = Path("tests/fixtures/sample_800x600.jpg")


@pytest.mark.asyncio
async def test_full_analysis_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with open(TEST_IMAGE, "rb") as f:
            r = await client.post(
                "/api/v1/images/upload", files={"file": ("sample.jpg", f, "image/jpeg")}
            )
        assert r.status_code == 200, f"Upload falló: {r.text}"
        analysis_id = r.json()["data"]["analysis_id"]
        assert len(analysis_id) == 36

        t0 = time.monotonic()
        r = await client.post(f"/api/v1/images/{analysis_id}/analyze")
        elapsed = time.monotonic() - t0
        assert r.status_code == 200, f"Analyze falló: {r.text}"
        assert elapsed < 5.0, f"RNF3 VIOLADO: análisis tardó {elapsed:.2f}s (límite: 5s)"

        result = r.json()["data"]
        assert "color_distribution" in result
        assert "stroke_metrics" in result
        assert "histogram" in result

        groups = result["color_distribution"]["therapeutic_groups"]
        assert "warm_pct" in groups and "cool_pct" in groups and "neutral_pct" in groups

        r = await client.get(f"/api/v1/reports/{analysis_id}/json")
        assert r.status_code == 200
        assert "color_distribution" in r.json()

        r = await client.get(f"/api/v1/reports/{analysis_id}/pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert len(r.content) > 1000


@pytest.mark.asyncio
async def test_invalid_format_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/v1/images/upload",
            files={"file": ("test.gif", b"GIF89a", "image/gif")},
        )
        assert r.status_code == 400
        assert r.json()["detail"]["code"] == "INVALID_FORMAT"


@pytest.mark.asyncio
async def test_analyze_nonexistent_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/v1/images/00000000-0000-0000-0000-000000000000/analyze"
        )
        assert r.status_code == 404
