import numpy as np
from app.core.pdi.region_detection import BlobRegion
from app.core.pdi.region_relations import compute_region_relationships


def _make_blob(region_id, centroid, mask_shape=(100, 100)):
    mask = np.zeros(mask_shape, dtype=np.uint8)
    cx, cy = int(centroid[0]), int(centroid[1])
    mask[max(0, cy-10):cy+10, max(0, cx-10):cx+10] = 255
    return BlobRegion(
        color_name="red",
        mask=mask,
        bbox=(cx - 10, cy - 10, 20, 20),
        polygon=np.array([]),
        centroid=(float(cx), float(cy)),
        area_pct=0.01,
        semiotic_zone="PASADO",
        region_id=region_id,
    )


def test_two_separate_regions_no_overlap():
    r1 = _make_blob("reg_001", (20, 20))
    r2 = _make_blob("reg_002", (80, 80))
    rels = compute_region_relationships([r1, r2])
    assert "reg_001" in rels
    assert "reg_002" in rels
    assert len(rels["reg_001"]["overlaps_with"]) == 0
    assert len(rels["reg_001"]["proximity_to"]) == 1
    assert rels["reg_001"]["proximity_to"][0]["region_id"] == "reg_002"


def test_two_overlapping_regions():
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[20:60, 20:60] = 255
    r1 = BlobRegion(
        color_name="red", mask=mask.copy(),
        bbox=(20, 20, 40, 40), polygon=np.array([]),
        centroid=(40.0, 40.0), area_pct=0.01,
        semiotic_zone="PASADO", region_id="reg_001",
    )
    r2 = BlobRegion(
        color_name="blue", mask=mask.copy(),
        bbox=(20, 20, 40, 40), polygon=np.array([]),
        centroid=(40.0, 40.0), area_pct=0.01,
        semiotic_zone="PASADO", region_id="reg_002",
    )
    rels = compute_region_relationships([r1, r2])
    assert "reg_002" in rels["reg_001"]["overlaps_with"]
    assert "reg_001" in rels["reg_002"]["overlaps_with"]


def test_three_regions_proximity():
    r1 = _make_blob("reg_001", (20, 20))
    r2 = _make_blob("reg_002", (80, 20))
    r3 = _make_blob("reg_003", (50, 80))
    rels = compute_region_relationships([r1, r2, r3])
    assert len(rels["reg_001"]["proximity_to"]) == 2
    assert len(rels["reg_002"]["proximity_to"]) == 2
    assert len(rels["reg_003"]["proximity_to"]) == 2


def test_layer_order_based_on_y():
    r1 = _make_blob("reg_001", (50, 10))
    r2 = _make_blob("reg_002", (50, 90))
    rels = compute_region_relationships([r1, r2])
    assert rels["reg_001"]["layer_order"] < rels["reg_002"]["layer_order"]


def test_empty_regions_list():
    rels = compute_region_relationships([])
    assert rels == {}
