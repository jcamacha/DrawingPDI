import time
from typing import List, Dict

from app.core.pdi.region_detection import BlobRegion, detect_color_blobs
from app.core.pdi.region_metrics import compute_region_metrics
from app.core.pdi.thumbnails import generate_region_thumbnail
from app.core.pdi.region_relations import compute_region_relationships
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
from app.core.pdi.spatial_analysis import SPATIAL_QUADRANTS

COLOR_EMPIRICAL_HINTS = {
    "red": "red: high arousal, activation, attention capture (Wilms & Oberfeld 2023; see cultural variability note)",
    "orange": "orange: moderate arousal, warmth, social affiliation (computational heuristic; Cha & Jung 2018)",
    "yellow": "yellow: positive valence, luminance-driven attention (computational heuristic; Cha & Jung 2018)",
    "green": "green: balanced valence-arousal, restorative association (computational heuristic; Cha & Jung 2018)",
    "blue": "blue: low arousal, calm, introspective tendency (computational heuristic; Cha & Jung 2018)",
    "violet": "violet: moderate arousal, imaginative association (computational heuristic; limited cross-cultural data)",
    "earth": "earth: grounding, corporeal connection, low-to-moderate arousal (computational heuristic; limited cross-cultural data)",
    "white": "white: achromatic, absence of pigment, potential avoidance or available space (computational heuristic)",
    "black": "black: achromatic, high contrast, density marker (computational heuristic)",
    "gray": "gray: achromatic, neutral, low chromatic engagement (computational heuristic)",
}

CHROMATIC_PROFILE_MAP = {
    "red_low": "warm", "red_high": "warm", "orange": "warm", "yellow": "warm", "earth": "warm",
    "green": "cool", "blue": "cool", "violet": "cool",
    "white": "neutral", "black": "neutral", "gray": "neutral",
}

INTERPRETATION_PROMPT_TEMPLATE = (
    "Based on the drawing analysis below, provide a DESCRIPTIVE (not diagnostic) "
    "report considering:\n"
    "1) The global quantitative VAD values and spatial distribution patterns observed.\n"
    "2) Each detected region's placement within its spatial quadrant (upper-left, "
    "upper-right, lower-left, lower-right) — described quantitatively, not interpreted.\n"
    "3) The empirical color-association references for each region. These are COMPUTATIONAL "
    "HEURISTICS with documented cultural variability (Cha & Jung 2018), NOT psychometric "
    "instruments. NEVER present them as clinical diagnoses.\n"
    "4) Relationships between regions (proximity, overlap, layering) — describe quantitatively.\n"
    "5) Graphomotor metrics (fragmentation, continuity, thickness) as quantitative "
    "descriptors of observable visual characteristics.\n\n"
    "Structure your response with:\n"
    "- A brief descriptive summary of the quantitative patterns observed.\n"
    "- Description of each significant region using measurable characteristics.\n"
    "- Identification of spatial patterns with their documented correlations (citing "
    "Lange-Küttner 2009 where applicable), always noting these are correlations, "
    "not causal relationships.\n"
    "- Observations about relationships between visual elements.\n"
    "- Areas that the therapist may wish to explore clinically, phrased as questions, "
    "not as conclusions.\n\n"
    "CRITICAL RULES:\n"
    "- NEVER state that a visual characteristic INDICATES or SUGGESTS a psychological "
    "state. Use language like 'correlates with', 'has been associated with', or "
    "'the therapist should evaluate whether...'\n"
    "- NEVER present computational heuristics (VAD, color associations) as diagnostic "
    "or psychometric instruments.\n"
    "- ALWAYS note that cultural variability affects color associations (Cha & Jung 2018).\n"
    "- This is an assistive tool that quantifies visual characteristics. ALL clinical "
    "interpretation must be performed by a qualified art therapist."
)


def _build_spatial_from_blob(blob: BlobRegion, image_width: int, image_height: int) -> AIRegionSpatial:
    x, y, w, h = blob.bbox
    polygon_points = blob.polygon.reshape(-1, 2).tolist() if blob.polygon.size > 0 else []

    h_mask, w_mask = blob.mask.shape[:2]
    half_h = h_mask // 2
    half_w = w_mask // 2
    total = max(float(__import__('cv2').countNonZero(blob.mask)), 1.0)
    tl = float(__import__('numpy').count_nonzero(blob.mask[:half_h, :half_w])) / total
    tr = float(__import__('numpy').count_nonzero(blob.mask[:half_h, half_w:])) / total
    bl = float(__import__('numpy').count_nonzero(blob.mask[half_h:, :half_w])) / total
    br = float(__import__('numpy').count_nonzero(blob.mask[half_h:, half_w:])) / total

    zone_desc = SPATIAL_QUADRANTS.get(blob.semiotic_zone, {}).get("description", "")

    return AIRegionSpatial(
        bounding_box=AIBoundingBox(x=x, y=y, width=w, height=h),
        polygon=AIPolygon(points=polygon_points),
        spatial_quadrant=blob.semiotic_zone,
        quadrant_description=zone_desc,
        quadrant_overlap=AIQuadrantOverlap(
            top_left_pct=round(tl, 4),
            top_right_pct=round(tr, 4),
            bottom_left_pct=round(bl, 4),
            bottom_right_pct=round(br, 4),
        ),
    )


def _build_local_metrics(metrics: dict) -> AIRegionLocalMetrics:
    color_dist = metrics.get("color_distribution")
    stroke = metrics.get("stroke_metrics")

    cd = None
    if color_dist:
        cd = ColorDistribution(
            specific=SpecificColors(**color_dist.get("specific", {})),
            therapeutic_groups=TherapeuticGroups(**color_dist.get("therapeutic_groups", {})),
        )

    sm = None
    if stroke:
        spatial = stroke.get("spatial_distribution", {})
        sm = StrokeMetrics(
            edge_density_pct=stroke.get("edge_density_pct", 0.0),
            mean_edge_intensity=stroke.get("mean_edge_intensity", 0.0),
            stroke_continuity=stroke.get("stroke_continuity", 0.0),
            fragmentation_ratio=stroke.get("fragmentation_ratio", 0.0),
            spatial_distribution=SpatialDistribution(
                top_left_pct=spatial.get("top_left_pct", 0.0),
                top_right_pct=spatial.get("top_right_pct", 0.0),
                bottom_left_pct=spatial.get("bottom_left_pct", 0.0),
                bottom_right_pct=spatial.get("bottom_right_pct", 0.0),
            ),
        )

    vad = metrics.get("vad_estimate", {})
    return AIRegionLocalMetrics(
        color_distribution=cd,
        stroke_metrics=sm,
        vad_estimate=ComputationalVAD(
            valence_estimate=vad.get("valence_estimate", 0.5),
            arousal_estimate=vad.get("arousal_estimate", 0.5),
            dominance_estimate=vad.get("dominance_estimate", 0.5),
        ),
        area_pct_of_canvas=metrics.get("area_pct_of_canvas", 0.0),
        compactness=metrics.get("compactness", 0.0),
        dominant_color=metrics.get("dominant_color", "unknown"),
    )


def _build_empirical_hints(blob: BlobRegion, dominant_color: str, chromatic_profile: str) -> AIEmpiricalHints:
    zone_desc = SPATIAL_QUADRANTS.get(blob.semiotic_zone, {}).get("description", "")
    color_hint = COLOR_EMPIRICAL_HINTS.get(dominant_color, "")

    zone_interpretations = {
        "PASADO": "Located in upper-left quadrant, associated with retrospective or memory-related content (Lange-Küttner 2009).",
        "FUTURO": "Located in upper-right quadrant, associated with prospective or aspiration-related content (Lange-Küttner 2009).",
        "MATERIAL": "Located in lower-left quadrant, associated with concrete or bodily concerns (Lange-Küttner 2009).",
        "IDEAL": "Located in lower-right quadrant, associated with imaginative or abstract ideation (Lange-Küttner 2009).",
    }
    spatial_interp = zone_interpretations.get(blob.semiotic_zone, "")

    return AIEmpiricalHints(
        chromatic_profile=chromatic_profile,
        quadrant_description=zone_desc,
        color_empirical_hints=[color_hint] if color_hint else [],
        spatial_interpretation=spatial_interp,
    )


def _build_relationships(rel_data: dict) -> AIRegionRelationships:
    proximity = []
    for p in rel_data.get("proximity_to", []):
        proximity.append(AIProximityRelation(
            region_id=p["region_id"],
            distance_px=p["distance_px"],
            direction=p["direction"],
        ))
    return AIRegionRelationships(
        overlaps_with=rel_data.get("overlaps_with", []),
        proximity_to=proximity,
        layer_order=rel_data.get("layer_order", 0),
    )


def _build_global_summary(analysis_result) -> AIGlobalClinicalSummary:
    ef = analysis_result.enriched_features
    sm = analysis_result.stroke_metrics
    cd = analysis_result.color_distribution

    vad = ComputationalVAD(valence_estimate=0.5, arousal_estimate=0.5, dominance_estimate=0.5)
    if ef and ef.computational_vad:
        vad = ef.computational_vad

    tone = "unknown"
    if cd and cd.therapeutic_groups:
        tg = cd.therapeutic_groups
        groups = {"warm": tg.warm_pct, "cool": tg.cool_pct, "neutral": tg.neutral_pct}
        tone = max(groups, key=groups.get)

    spatial_bias = "balanced"
    if sm and sm.spatial_distribution:
        sd = sm.spatial_distribution
        quadrants = {
            "top-left": sd.top_left_pct,
            "top-right": sd.top_right_pct,
            "bottom-left": sd.bottom_left_pct,
            "bottom-right": sd.bottom_right_pct,
        }
        max_q = max(quadrants, key=quadrants.get)
        max_val = quadrants[max_q]
        if max_val > 0.35:
            spatial_bias = max_q

    frag_level = "unknown"
    if sm:
        fr = sm.fragmentation_ratio
        if fr < 0.2:
            frag_level = "low"
        elif fr < 0.5:
            frag_level = "moderate"
        else:
            frag_level = "high"

    total_colored = 0.0
    if cd:
        s = cd.specific
        total_colored = round(
            1.0 - s.white_pct - s.black_pct - s.gray_pct - s.other_pct, 4
        )

    return AIGlobalClinicalSummary(
        dominant_emotional_tone=tone,
        overall_vad=vad,
        spatial_bias=spatial_bias,
        fragmentation_level=frag_level,
        total_colored_area_pct=total_colored,
    )


def build_ai_context(
    image_array,
    canny_array,
    analysis_result,
    min_area_pct: float = 0.005,
    max_regions: int = 30,
) -> AIContext:
    start = time.monotonic()

    h, w = image_array.shape[:2]

    blobs = detect_color_blobs(image_array, min_area_pct=min_area_pct, max_regions=max_regions)

    rel_data = compute_region_relationships(blobs)

    regions: List[DetectedRegion] = []
    for blob in blobs:
        metrics = compute_region_metrics(image_array, blob)
        thumbnail = generate_region_thumbnail(image_array, blob.bbox)
        therapeutic_group = CHROMATIC_PROFILE_MAP.get(blob.color_name, "unknown")

        region = DetectedRegion(
            region_id=blob.region_id,
            detection_method="color_blob",
            label=f"{blob.color_name}_blob",
            confidence=1.0,
            spatial=_build_spatial_from_blob(blob, w, h),
            local_metrics=_build_local_metrics(metrics),
            empirical_hints=_build_empirical_hints(blob, metrics.get("dominant_color", "unknown"), therapeutic_group),
            relationships=_build_relationships(rel_data.get(blob.region_id, {})),
            thumbnail_b64=thumbnail,
        )
        regions.append(region)

    global_summary = _build_global_summary(analysis_result)

    meta = AIMeta(
        analysis_id=analysis_result.analysis_id,
        timestamp=analysis_result.timestamp,
        image_dimensions={"width": w, "height": h},
        pipeline_version="3.0-digital-phenotyping",
    )

    elapsed = time.monotonic() - start

    return AIContext(
        meta=meta,
        global_context=global_summary,
        regions=regions,
        interpretation_prompt_template=INTERPRETATION_PROMPT_TEMPLATE,
    ), elapsed
