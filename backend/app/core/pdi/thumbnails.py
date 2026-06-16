import base64
import cv2
import numpy as np
from typing import Tuple


def _pad_to_square(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    if h == w:
        return image
    size = max(h, w)
    square = np.zeros((size, size, 3), dtype=np.uint8)
    y_offset = (size - h) // 2
    x_offset = (size - w) // 2
    square[y_offset:y_offset + h, x_offset:x_offset + w] = image
    return square


def generate_region_thumbnail(
    image: np.ndarray,
    bbox: Tuple[int, int, int, int],
    size: int = 224,
) -> str:
    x, y, w, h = bbox

    x = max(0, x)
    y = max(0, y)
    w = max(1, w)
    h = max(1, h)

    img_h, img_w = image.shape[:2]
    x = min(x, img_w - 1)
    y = min(y, img_h - 1)
    w = min(w, img_w - x)
    h = min(h, img_h - y)

    if w <= 0 or h <= 0:
        blank = np.zeros((size, size, 3), dtype=np.uint8)
        _, buffer = cv2.imencode(".png", blank)
        return base64.b64encode(buffer).decode("utf-8")

    crop = image[y:y + h, x:x + w]

    if crop.shape[0] < 10 or crop.shape[1] < 10:
        interpolation = cv2.INTER_CUBIC
    else:
        interpolation = cv2.INTER_AREA

    square = _pad_to_square(crop)
    thumbnail = cv2.resize(square, (size, size), interpolation=interpolation)

    _, buffer = cv2.imencode(".png", thumbnail)
    return base64.b64encode(buffer).decode("utf-8")
