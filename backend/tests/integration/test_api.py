import io
import base64

import numpy as np
import cv2
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.pdi import session


def _create_test_image_b64(width=100, height=100):
    img = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    return base64.b64encode(buffer).decode("utf-8")


@pytest.mark.asyncio
async def test_upload_valid_jpg():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        files = {"file": ("test.jpg", buffer.tobytes(), "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert "analysis_id" in data["data"]
        assert len(data["data"]["analysis_id"]) == 36


@pytest.mark.asyncio
async def test_upload_invalid_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.gif", b"GIF89a", "image/gif")}
        r = await client.post("/api/v1/images/upload", files=files)
        assert r.status_code == 400
        assert r.json()["detail"]["code"] == "INVALID_FORMAT"


@pytest.mark.asyncio
async def test_upload_empty_file():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.jpg", b"", "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        assert r.status_code == 400


@pytest.mark.asyncio
async def test_upload_file_too_large():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        big_content = b"x" * (11 * 1024 * 1024)
        files = {"file": ("test.jpg", big_content, "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        assert r.status_code == 400
        assert r.json()["detail"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_analyze_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        files = {"file": ("test.jpg", buffer.tobytes(), "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.post(f"/api/v1/images/{analysis_id}/analyze")
        assert r.status_code == 200
        data = r.json()["data"]
        assert "color_distribution" in data
        assert "stroke_metrics" in data
        assert "histogram" in data
        assert "images" in data


@pytest.mark.asyncio
async def test_analyze_nonexistent_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/v1/images/00000000-0000-0000-0000-000000000000/analyze"
        )
        assert r.status_code == 404


@pytest.mark.asyncio
async def test_report_json():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        files = {"file": ("test.jpg", buffer.tobytes(), "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        analysis_id = r.json()["data"]["analysis_id"]

        await client.post(f"/api/v1/images/{analysis_id}/analyze")

        r = await client.get(f"/api/v1/reports/{analysis_id}/json")
        assert r.status_code == 200
        assert "color_distribution" in r.json()


@pytest.mark.asyncio
async def test_report_json_incomplete():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        files = {"file": ("test.jpg", buffer.tobytes(), "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.get(f"/api/v1/reports/{analysis_id}/json")
        assert r.status_code == 409


@pytest.mark.asyncio
async def test_report_pdf():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        files = {"file": ("test.jpg", buffer.tobytes(), "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        analysis_id = r.json()["data"]["analysis_id"]

        await client.post(f"/api/v1/images/{analysis_id}/analyze")

        r = await client.get(f"/api/v1/reports/{analysis_id}/pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert len(r.content) > 1000


@pytest.mark.asyncio
async def test_report_pdf_incomplete():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".jpg", img)
        files = {"file": ("test.jpg", buffer.tobytes(), "image/jpeg")}
        r = await client.post("/api/v1/images/upload", files=files)
        analysis_id = r.json()["data"]["analysis_id"]

        r = await client.get(f"/api/v1/reports/{analysis_id}/pdf")
        assert r.status_code == 409
