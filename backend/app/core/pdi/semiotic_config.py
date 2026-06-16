import warnings
from app.core.pdi.spatial_analysis import (
    SPATIAL_QUADRANTS,
    SEMIOTIC_ZONES,
    classify_spatial_zone,
    classify_semiotic_zone,
)

warnings.warn(
    "semiotic_config is deprecated. Use spatial_analysis instead.",
    DeprecationWarning,
    stacklevel=2,
)