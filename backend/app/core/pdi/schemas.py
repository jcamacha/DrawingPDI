from pydantic import BaseModel
from typing import Optional, List


class SpecificColors(BaseModel):
    red_pct: float = 0.0
    orange_pct: float = 0.0
    yellow_pct: float = 0.0
    green_pct: float = 0.0
    blue_pct: float = 0.0
    violet_pct: float = 0.0
    earth_pct: float = 0.0
    white_pct: float = 0.0
    black_pct: float = 0.0
    gray_pct: float = 0.0
    other_pct: float = 0.0


class TherapeuticGroups(BaseModel):
    warm_pct: float = 0.0
    cool_pct: float = 0.0
    neutral_pct: float = 0.0
    other_pct: float = 0.0


class ColorDistribution(BaseModel):
    specific: SpecificColors
    therapeutic_groups: TherapeuticGroups


class SpatialDistribution(BaseModel):
    top_left_pct: float = 0.0
    top_right_pct: float = 0.0
    bottom_left_pct: float = 0.0
    bottom_right_pct: float = 0.0


class StrokeMetrics(BaseModel):
    edge_density_pct: float = 0.0
    mean_edge_intensity: float = 0.0
    stroke_continuity: float = 0.0
    fragmentation_ratio: float = 0.0
    spatial_distribution: SpatialDistribution = SpatialDistribution()
    edge_thickness_px: float = 0.0
    graphomotor_stability: float = 0.0


class ColorHistogram(BaseModel):
    hue: List[int] = []
    saturation: List[int] = []
    value: List[int] = []


class ComputationalVAD(BaseModel):
    valence_estimate: float = 0.0
    arousal_estimate: float = 0.0
    dominance_estimate: float = 0.0


class ChromaticCentroid(BaseModel):
    x_norm: float = 0.5
    y_norm: float = 0.5


class SpatialPhenotype(BaseModel):
    dominant_group: str = "unknown"
    predominant_color_centroid: ChromaticCentroid = ChromaticCentroid()
    quadrant_mass_distribution: SpatialDistribution = SpatialDistribution()


SemioticMass = SpatialPhenotype


class CanvasUtilization(BaseModel):
    total_used_pct: float = 0.0
    expansion_flag: str = "normal"
    symmetry_index: float = 0.0


class VisualComplexity(BaseModel):
    fractal_dimension: float = 0.0
    image_entropy: float = 0.0
    organization_level: str = "unknown"


class GraphomotorProfile(BaseModel):
    edge_density_pct: float = 0.0
    fragmentation_ratio: float = 0.0
    stroke_continuity: float = 0.0
    edge_thickness_px: float = 0.0
    graphomotor_stability: float = 0.0


class EnrichedFeatures(BaseModel):
    computational_vad: ComputationalVAD = ComputationalVAD()
    spatial_phenotype: SpatialPhenotype = SpatialPhenotype()
    canvas_utilization: CanvasUtilization = CanvasUtilization()
    visual_complexity: VisualComplexity = VisualComplexity()
    graphomotor_profile: GraphomotorProfile = GraphomotorProfile()

    model_config = {"populate_by_name": True}

    @property
    def semiotic_mass(self) -> SpatialPhenotype:
        return self.spatial_phenotype


class DetectedSymbol(BaseModel):
    symbol_class: str
    confidence: float
    bounding_box: dict
    spatial_quadrant: str
    symbol_metrics: Optional[dict] = None


class ProcessedImages(BaseModel):
    original_b64: str
    filtered_b64: Optional[str] = None
    canny_b64: Optional[str] = None
    hsv_mask_b64: Optional[str] = None


class AnalysisResult(BaseModel):
    analysis_id: str
    timestamp: str
    color_distribution: Optional[ColorDistribution] = None
    stroke_metrics: Optional[StrokeMetrics] = None
    histogram: Optional[ColorHistogram] = None
    enriched_features: Optional[EnrichedFeatures] = None
    detected_symbols: List[DetectedSymbol] = []
    images: ProcessedImages


class AIBoundingBox(BaseModel):
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


class AIPolygon(BaseModel):
    points: List[List[int]] = []


class AIQuadrantOverlap(BaseModel):
    top_left_pct: float = 0.0
    top_right_pct: float = 0.0
    bottom_left_pct: float = 0.0
    bottom_right_pct: float = 0.0


class AIRegionSpatial(BaseModel):
    bounding_box: AIBoundingBox = AIBoundingBox()
    polygon: AIPolygon = AIPolygon()
    spatial_quadrant: str = ""
    quadrant_description: str = ""
    quadrant_overlap: AIQuadrantOverlap = AIQuadrantOverlap()


class AIRegionLocalMetrics(BaseModel):
    color_distribution: Optional[ColorDistribution] = None
    stroke_metrics: Optional[StrokeMetrics] = None
    vad_estimate: ComputationalVAD = ComputationalVAD()
    area_pct_of_canvas: float = 0.0
    compactness: float = 0.0
    dominant_color: str = "unknown"


class AIProximityRelation(BaseModel):
    region_id: str = ""
    distance_px: float = 0.0
    direction: str = ""


class AIRegionRelationships(BaseModel):
    overlaps_with: List[str] = []
    proximity_to: List[AIProximityRelation] = []
    layer_order: int = 0


class AIEmpiricalHints(BaseModel):
    chromatic_profile: str = ""
    quadrant_description: str = ""
    color_empirical_hints: List[str] = []
    spatial_interpretation: str = ""


AISemioticHints = AIEmpiricalHints


class DetectedRegion(BaseModel):
    region_id: str = ""
    detection_method: str = "color_blob"
    label: Optional[str] = None
    confidence: float = 1.0
    spatial: AIRegionSpatial = AIRegionSpatial()
    local_metrics: AIRegionLocalMetrics = AIRegionLocalMetrics()
    empirical_hints: AIEmpiricalHints = AIEmpiricalHints()
    relationships: AIRegionRelationships = AIRegionRelationships()
    thumbnail_b64: str = ""


class AIGlobalClinicalSummary(BaseModel):
    dominant_emotional_tone: str = "unknown"
    overall_vad: ComputationalVAD = ComputationalVAD()
    spatial_bias: str = "balanced"
    fragmentation_level: str = "unknown"
    total_colored_area_pct: float = 0.0


class AIMeta(BaseModel):
    analysis_id: str = ""
    timestamp: str = ""
    image_dimensions: dict = {"width": 0, "height": 0}
    pipeline_version: str = "3.0-digital-phenotyping"


class AIContext(BaseModel):
    meta: AIMeta = AIMeta()
    global_context: AIGlobalClinicalSummary = AIGlobalClinicalSummary()
    regions: List[DetectedRegion] = []
    interpretation_prompt_template: str = ""