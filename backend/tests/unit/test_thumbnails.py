import base64
import cv2
import numpy as np
from app.core.pdi.thumbnails import generate_region_thumbnail


def test_thumbnail_valid_base64():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    b64 = generate_region_thumbnail(img, (50, 50, 100, 100))
    decoded = base64.b64decode(b64)
    assert len(decoded) > 0


def test_thumbnail_decodable_as_image():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    b64 = generate_region_thumbnail(img, (50, 50, 100, 100))
    decoded = base64.b64decode(b64)
    arr = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
    assert arr is not None
    assert arr.shape[0] == 224 and arr.shape[1] == 224


def test_thumbnail_small_crop():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    b64 = generate_region_thumbnail(img, (100, 100, 5, 5))
    decoded = base64.b64decode(b64)
    arr = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
    assert arr.shape[0] == 224 and arr.shape[1] == 224


def test_thumbnail_out_of_bounds():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    b64 = generate_region_thumbnail(img, (90, 90, 50, 50))
    decoded = base64.b64decode(b64)
    arr = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
    assert arr is not None


def test_thumbnail_custom_size():
    img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    b64 = generate_region_thumbnail(img, (50, 50, 100, 100), size=128)
    decoded = base64.b64decode(b64)
    arr = cv2.imdecode(np.frombuffer(decoded, np.uint8), cv2.IMREAD_COLOR)
    assert arr.shape[0] == 128 and arr.shape[1] == 128
