import numpy as np
from app.core.pdi.filters import (
    apply_gaussian_filter,
    apply_bilateral_filter,
    ndarray_to_base64,
)


def test_gaussian_same_shape():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = apply_gaussian_filter(img)
    assert result.shape == img.shape


def test_gaussian_changes_content():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = apply_gaussian_filter(img)
    assert not np.array_equal(result, img)


def test_bilateral_same_shape():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = apply_bilateral_filter(img)
    assert result.shape == img.shape


def test_ndarray_to_base64_returns_string():
    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = ndarray_to_base64(img)
    assert isinstance(result, str)
    assert len(result) > 0
