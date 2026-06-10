from pydantic import BaseModel
from typing import Optional, List


class SpecificColors(BaseModel):
    red_pct: float = 0.0
    orange_pct: float = 0.0
    yellow_pct: float = 0.0
    green_pct: float = 0.0
    blue_pct: float = 0.0
    violet_pct: float = 0.0
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


class SemioticMass(BaseModel):
    dominant_group: str = "unknown"
    predominant_color_centroid: ChromaticCentroid = ChromaticCentroid()
    quadrant_mass_distribution: SpatialDistribution = SpatialDistribution()


class EnrichedFeatures(BaseModel):
    computational_vad: ComputationalVAD = ComputationalVAD()
    semiotic_mass: SemioticMass = SemioticMass()


class DetectedSymbol(BaseModel):
    symbol_class: str
    confidence: float
    bounding_box: dict
    semiotic_zone: str
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