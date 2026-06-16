SPATIAL_QUADRANTS = {
    "PASADO": {
        "x_range": (0.0, 0.5),
        "y_range": (0.0, 0.5),
        "description": "Upper-left quadrant. Concentration of visual content in this area correlates with constrained expression and low psychomotor activation (Lange-Kuttner, 2009; Broadbent et al., 2019).",
        "clinical_indicators": "Low spatial utilization in this quadrant may indicate inhibition or restricted emotional expression.",
    },
    "FUTURO": {
        "x_range": (0.5, 1.0),
        "y_range": (0.0, 0.5),
        "description": "Upper-right quadrant. Visual content here suggests forward-oriented spatial distribution and planning tendencies.",
        "clinical_indicators": "Higher utilization of this quadrant may reflect expansive or externally-directed expression.",
    },
    "MATERIAL": {
        "x_range": (0.0, 0.5),
        "y_range": (0.5, 1.0),
        "description": "Lower-left quadrant. Content placement here reflects grounding spatial distribution patterns.",
        "clinical_indicators": "Predominant weighting in this quadrant may indicate stability or grounding tendencies.",
    },
    "IDEAL": {
        "x_range": (0.5, 1.0),
        "y_range": (0.5, 1.0),
        "description": "Lower-right quadrant. Spatial concentration here is associated with expansive use of the drawing canvas.",
        "clinical_indicators": "Overwhelming presence in this quadrant may correlate with expansive psychomotor states.",
    },
}


SEMIOTIC_ZONES = SPATIAL_QUADRANTS


def classify_spatial_zone(x_norm: float, y_norm: float) -> str:
    x = max(0.0, min(1.0, float(x_norm)))
    y = max(0.0, min(1.0, float(y_norm)))

    if x < 0.5 and y < 0.5:
        return "PASADO"
    elif x >= 0.5 and y < 0.5:
        return "FUTURO"
    elif x < 0.5 and y >= 0.5:
        return "MATERIAL"
    else:
        return "IDEAL"


def classify_semiotic_zone(x_norm: float, y_norm: float) -> str:
    return classify_spatial_zone(x_norm, y_norm)