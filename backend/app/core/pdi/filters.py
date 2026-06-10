import cv2
import numpy as np
import base64


def apply_gaussian_filter(
    image: np.ndarray,
    kernel_size: tuple = (5, 5),
    sigma_x: float = 0.0,
) -> np.ndarray:
    return cv2.GaussianBlur(image, kernel_size, sigma_x)


def apply_bilateral_filter(
    image: np.ndarray,
    d: int = 9,
    sigma_color: float = 75.0,
    sigma_space: float = 75.0,
) -> np.ndarray:
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def ndarray_to_base64(image: np.ndarray, ext: str = ".png") -> str:
    _, buffer = cv2.imencode(ext, image)
    return base64.b64encode(buffer).decode("utf-8")
