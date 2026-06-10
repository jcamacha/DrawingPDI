SEMIOTIC_ZONES = {
    "PASADO": {
        "x_range": (0.0, 0.5),
        "y_range": (0.0, 0.5),
        "description": "Zona del pasado. Elementos vinculados a memoria, experiencias previas y afectividad temprana.",
    },
    "FUTURO": {
        "x_range": (0.5, 1.0),
        "y_range": (0.0, 0.5),
        "description": "Zona del futuro. Elementos vinculados a aspiraciones, expectativas y proyección temporal.",
    },
    "MATERIAL": {
        "x_range": (0.0, 0.5),
        "y_range": (0.5, 1.0),
        "description": "Zona material. Elementos vinculados a lo concreto, lo terrenal y las necesidades básicas.",
    },
    "IDEAL": {
        "x_range": (0.5, 1.0),
        "y_range": (0.5, 1.0),
        "description": "Zona ideal. Elementos vinculados a lo abstracto, lo espiritual y las aspiraciones superiores.",
    },
}


def classify_semiotic_zone(x_norm: float, y_norm: float) -> str:
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