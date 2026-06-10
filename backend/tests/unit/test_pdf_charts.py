"""
test_pdf_charts.py — Tests unitarios para pdf_charts.py (PDI-24)
Verifica que cada función retorne Drawing y no lance excepciones,
incluyendo valores en límite (0.0, 0.5, 1.0).
"""

from reportlab.graphics.shapes import Drawing

from app.api.v1.pdf_charts import (
    build_vad_bar_chart,
    build_therapeutic_pie,
    build_koch_diagram,
    build_spatial_bar,
)
from app.core.pdi.schemas import ComputationalVAD, TherapeuticGroups, SpatialDistribution


def test_vad_bar_chart_returns_drawing():
    """Verifica que build_vad_bar_chart retorna un Drawing con valores normales."""
    vad = ComputationalVAD(valence_estimate=0.7, arousal_estimate=0.4, dominance_estimate=0.5)
    result = build_vad_bar_chart(vad)
    assert isinstance(result, Drawing)


def test_therapeutic_pie_returns_drawing():
    """Verifica que build_therapeutic_pie retorna un Drawing con valores válidos."""
    groups = TherapeuticGroups(warm_pct=0.5, cool_pct=0.3, neutral_pct=0.2, other_pct=0.0)
    result = build_therapeutic_pie(groups)
    assert isinstance(result, Drawing)


def test_therapeutic_pie_all_zeros_no_exception():
    """Caso límite: todo cero excepto un grupo — no debe lanzar excepción."""
    groups = TherapeuticGroups(warm_pct=1.0, cool_pct=0.0, neutral_pct=0.0, other_pct=0.0)
    result = build_therapeutic_pie(groups)
    assert isinstance(result, Drawing)


def test_koch_diagram_returns_drawing():
    """Verifica que build_koch_diagram retorna un Drawing con valores típicos."""
    result = build_koch_diagram(0.3, 0.7, "MATERIAL")
    assert isinstance(result, Drawing)


def test_koch_diagram_boundary_values():
    """Caso límite: centroide en (0.0, 0.0) — no debe salir del canvas."""
    result = build_koch_diagram(0.0, 0.0, "PASADO")
    assert isinstance(result, Drawing)


def test_spatial_bar_returns_drawing():
    """Verifica que build_spatial_bar retorna un Drawing con distribución uniforme."""
    dist = SpatialDistribution(
        top_left_pct=0.25,
        top_right_pct=0.25,
        bottom_left_pct=0.25,
        bottom_right_pct=0.25,
    )
    result = build_spatial_bar(dist)
    assert isinstance(result, Drawing)
