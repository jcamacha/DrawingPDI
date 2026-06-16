import numpy as np
from app.core.pdi.schemas import (
    AIContext,
    AIMeta,
    AIGlobalClinicalSummary,
    DetectedRegion,
    AIRegionSpatial,
    AIBoundingBox,
    AIPolygon,
    AIQuadrantOverlap,
    AIRegionLocalMetrics,
    AIEmpiricalHints,
    AIRegionRelationships,
    AIProximityRelation,
    ComputationalVAD,
    ColorDistribution,
    SpecificColors,
    TherapeuticGroups,
    StrokeMetrics,
    SpatialDistribution,
)


def test_ai_context_default_creation():
    ctx = AIContext()
    assert ctx.meta is not None
    assert ctx.global_context is not None
    assert ctx.regions == []
    assert ctx.interpretation_prompt_template == ""


def test_ai_context_model_dump():
    ctx = AIContext()
    dump = ctx.model_dump()
    assert "meta" in dump
    assert "global_context" in dump
    assert "regions" in dump
    assert "interpretation_prompt_template" in dump


def test_detected_region_full():
    region = DetectedRegion(
        region_id="reg_001",
        detection_method="color_blob",
        label="red_blob",
        confidence=1.0,
        spatial=AIRegionSpatial(
            bounding_box=AIBoundingBox(x=10, y=20, width=100, height=80),
            polygon=AIPolygon(points=[[10, 20], [110, 20], [110, 100], [10, 100]]),
            spatial_quadrant="PASADO",
            quadrant_description="Upper-left quadrant.",
            quadrant_overlap=AIQuadrantOverlap(
                top_left_pct=0.8, top_right_pct=0.2,
                bottom_left_pct=0.0, bottom_right_pct=0.0,
            ),
        ),
        local_metrics=AIRegionLocalMetrics(
            dominant_color="red",
            compactness=0.75,
            area_pct_of_canvas=0.15,
        ),
        empirical_hints=AIEmpiricalHints(
            chromatic_profile="warm",
            quadrant_description="Upper-left quadrant.",
            color_empirical_hints=["red: high arousal, activation, attention capture"],
            spatial_interpretation="Located in upper-left quadrant.",
        ),
        relationships=AIRegionRelationships(
            overlaps_with=["reg_002"],
            proximity_to=[AIProximityRelation(
                region_id="reg_002",
                distance_px=50.0,
                direction="bottom-right",
            )],
            layer_order=20,
        ),
        thumbnail_b64="fake_base64",
    )
    dump = region.model_dump()
    assert dump["region_id"] == "reg_001"
    assert dump["spatial"]["spatial_quadrant"] == "PASADO"
    assert dump["local_metrics"]["dominant_color"] == "red"
    assert len(dump["relationships"]["proximity_to"]) == 1


def test_ai_context_with_regions():
    ctx = AIContext(
        meta=AIMeta(
            analysis_id="test-uuid",
            timestamp="2026-01-01T00:00:00",
            image_dimensions={"width": 800, "height": 600},
            pipeline_version="3.0-digital-phenotyping",
        ),
        global_context=AIGlobalClinicalSummary(
            dominant_emotional_tone="warm",
            overall_vad=ComputationalVAD(
                valence_estimate=0.7, arousal_estimate=0.6, dominance_estimate=0.5,
            ),
            spatial_bias="top-left",
            fragmentation_level="moderate",
            total_colored_area_pct=0.45,
        ),
        regions=[
            DetectedRegion(region_id="reg_001", label="red_blob"),
            DetectedRegion(region_id="reg_002", label="blue_blob"),
        ],
        interpretation_prompt_template="Test prompt",
    )
    dump = ctx.model_dump()
    assert dump["meta"]["analysis_id"] == "test-uuid"
    assert len(dump["regions"]) == 2
    assert dump["global_context"]["dominant_emotional_tone"] == "warm"


def test_ai_context_zero_regions_valid():
    ctx = AIContext(
        meta=AIMeta(analysis_id="test"),
        regions=[],
    )
    dump = ctx.model_dump()
    assert dump["regions"] == []
