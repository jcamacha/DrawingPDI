"""
reports.py — PDI-25
Endpoints de generación de reportes cuantitativos PDF y JSON para Arteterapia.
Refactorización completa con 7 secciones narrativas y gráficos ReportLab.

Endpoints disponibles:
    GET /reports/{analysis_id}/json  — Datos de análisis en formato JSON
    GET /reports/{analysis_id}/pdf   — Reporte cuantitativo en PDF con gráficos
"""

import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Flowable,
    HRFlowable,
)
from reportlab.graphics import renderPDF

from app.core.pdi import session
from app.api.v1.pdf_charts import (
    build_vad_bar_chart,
    build_therapeutic_pie,
    build_quadrant_diagram,
    build_spatial_bar,
)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Clase auxiliar para embeber objetos Drawing de ReportLab en Platypus
# ─────────────────────────────────────────────────────────────────────────────
class DrawingFlowable(Flowable):
    """
    Envuelve un objeto Drawing de reportlab.graphics en un Platypus Flowable
    para poder insertarlo dentro de un SimpleDocTemplate.
    """

    def __init__(self, drawing):
        super().__init__()
        self.drawing = drawing
        self.width = drawing.width
        self.height = drawing.height

    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)


# ─────────────────────────────────────────────────────────────────────────────
# Glosarios descriptivos para el reporte cuantitativo
# NOTA: Todo lenguaje es descriptivo, no concluyente ni diagnóstico.
# La interpretación psicológica es responsabilidad exclusiva del terapeuta.
# ─────────────────────────────────────────────────────────────────────────────
GLOSARIO_VAD = {
    "valence_high": (
        "La composición cromática presenta predominancia de colores computacionalmente "
        "asociados a valencia positiva (VAD > 0.6). Esto refleja la distribución de "
        "tonos observada; la significación emocional debe ser evaluada por el terapeuta "
        "en el contexto clínico específico. Nota: las asociaciones de color presentan "
        "variabilidad cultural documentada (Cha & Jung 2018)."
    ),
    "valence_low": (
        "La composición cromática presenta predominancia de tonos computacionalmente "
        "asociados a valencia baja o de tensión. Se recomienda evaluar si existen "
        "focos de alto contraste o elementos atípicos antes de atribuir significación "
        "clínica. Las asociaciones VAD son heurísticas computacionales, no instrumentos "
        "psicométricos."
    ),
    "arousal_high": (
        "Los valores cromáticos indican alta saturación de tonos activadores (VAD Arousal "
        "> 0.5). El clínico debe considerar si la activación es difusa o focalizada, "
        "y contextualizarla con la observación directa del proceso creativo. Las asociaciones "
        "color-arousal son heurísticas con variabilidad cultural (Cha & Jung 2018)."
    ),
    "arousal_low": (
        "La composición cromática presenta baja saturación de tonos activadores (VAD Arousal "
        "< 0.5). El terapeuta puede explorar si esto corresponde a contención, fatiga o "
        "selección deliberada de tonos apagados, en el contexto de la sesión."
    ),
}

GLOSARIO_CUADRANTES = {
    "PASADO": (
        "La concentración de masa cromática en el cuadrante superior izquierdo "
        "cuantifica la distribución espacial observada. Estudios de Lange-Küttner (2009) "
        "documentan que la ubicación superior-izquierda correlaciona con contenido "
        "retrospectivo en ciertas poblaciones; la significación clínica específica "
        "debe evaluarse en contexto."
    ),
    "FUTURO": (
        "La concentración de masa cromática en el cuadrante superior derecho "
        "cuantifica la distribución espacial observada. Lange-Küttner (2009) documenta "
        "asociaciones con contenido prospectivo o aspiracional; esta correlación no "
        "constituye un diagnóstico y debe validarse clínicamente."
    ),
    "MATERIAL": (
        "La concentración de masa cromática en el cuadrante inferior izquierdo "
        "cuantifica la distribución espacial observada. Lange-Küttner (2009) documenta "
        "asociaciones con contenido concreto o corporal; la interpretación psicológica "
        "es responsabilidad del terapeuta en el contexto de la sesión."
    ),
    "IDEAL": (
        "La concentración de masa cromática en el cuadrante inferior derecho "
        "cuantifica la distribución espacial observada. Lange-Küttner (2009) documenta "
        "asociaciones con contenido imaginativo o abstracto; esta correlación espacial "
        "no constituye por sí misma un indicador diagnóstico."
    ),
}

GLOSARIO_TRAZO = {
    "frag_high": (
        "Se observa alta fragmentación de trazo (ratio > 0.5): los gestos son cortos "
        "e interrumpidos. Esto puede corresponder a diversos factores (exploración "
        "cautelosa, estilo personal, ansiedad motriz, entre otros); el terapeuta debe "
        "interpretar en el contexto clínico específico."
    ),
    "frag_mid": (
        "Se documenta fragmentación moderada del trazo (0.3 < ratio < 0.5). Esta "
        "observación cuantitativa describe la continuidad de los bordes detectados; "
        "la significación clínica depende del contexto terapéutico."
    ),
    "frag_low": (
        "El trazo presenta baja fragmentación (ratio < 0.3), con gestos continuos. "
        "Esta medición cuantitativa no constituye por sí misma un indicador diagnóstico; "
        "la interpretación corresponde al terapeuta."
    ),
}

DISCLAIMER_GLOBAL = (
    "<b>AVISO IMPORTANTE:</b> Este reporte presenta cuantificadores de características visuales "
    "extraídos por algoritmos de procesamiento digital de imagen. No constituye un instrumento "
    "diagnóstico ni psicométrico. Las asociaciones de color (VAD) son heurísticas computacionales "
    "con variabilidad cultural documentada (Cha & Jung 2018). La interpretación psicológica es "
    "responsabilidad exclusiva del terapeuta calificado en el contexto clínico específico."
)


# ─────────────────────────────────────────────────────────────────────────────
# Funciones auxiliares de construcción de secciones del PDF
# ─────────────────────────────────────────────────────────────────────────────

def _estilo_tabla_base():
    """Retorna el TableStyle estándar para todas las tablas del reporte."""
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a4a4a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ])


def _cell_paragraph(text, style_name="cell_text", font_size=9, text_color=colors.HexColor("#333333")):
    """Convierte texto plano en un Paragraph con word-wrap para celdas de tabla."""
    style = ParagraphStyle(
        style_name,
        fontSize=font_size,
        leading=font_size + 3,
        textColor=text_color,
    )
    return Paragraph(text, style)


def _seccion1_encabezado(elements, styles, analysis_id, timestamp):
    """
    SECCIÓN 1 — Encabezado institucional con título, subtítulo, ID y separador.
    """
    estilo_subtitulo = ParagraphStyle(
        "subtitulo",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        spaceAfter=8,
    )

    elements.append(Paragraph("Reporte Cuantitativo de Características Visuales — PDI", styles["Title"]))
    elements.append(Paragraph(
        "Cuantificación de características visuales de la producción artística. "
        "Para interpretación clínica, consultar al terapeuta responsable.",
        estilo_subtitulo,
    ))

    # Disclaimer global
    estilo_disclaimer = ParagraphStyle(
        "disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#8b0000"),
        backColor=colors.HexColor("#fff8f8"),
        borderColor=colors.HexColor("#d4a0a0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=10,
    )
    elements.append(Paragraph(DISCLAIMER_GLOBAL, estilo_disclaimer))

    # Tabla de metadatos básicos
    meta_data = [
        ["ID de Análisis", analysis_id],
        ["Fecha de Generación", timestamp],
    ]
    meta_table = Table(meta_data, colWidths=[5 * cm, 12 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#333333")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 0.4 * cm))


def _seccion2_resumen_ejecutivo(elements, styles, s):
    """
    SECCIÓN 2 — Resumen cuantitativo descriptivo (sin interpretación diagnóstica).
    Genera un párrafo narrativo basado en los estimados VAD y métricas de trazo.
    Todo lenguaje es descriptivo, no concluyente.
    """
    estilo_resumen = ParagraphStyle(
        "resumen",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        borderPad=8,
        backColor=colors.HexColor("#f5f5f0"),
        borderColor=colors.HexColor("#cccccc"),
        borderWidth=0.5,
        borderRadius=4,
    )

    ef = s.enriched_features
    sm = s.stroke_metrics

    if ef and ef.computational_vad.arousal_estimate > 0.6:
        intensidad = "alta presencia de tonos cromáticos activadores (VAD Arousal > 0.6)"
    elif ef and ef.computational_vad.arousal_estimate > 0.4:
        intensidad = "presencia moderada de tonos activadores (VAD Arousal 0.4–0.6)"
    else:
        intensidad = "baja presencia de tonos cromáticos activadores (VAD Arousal < 0.4)"

    if ef and ef.computational_vad.valence_estimate > 0.6:
        tono = "con predominancia de colores computacionalmente asociados a valencia positiva"
    elif ef and ef.computational_vad.valence_estimate > 0.4:
        tono = "con distribución cromática de valencia intermedia"
    else:
        tono = "con predominancia cromática asociada a valencia baja o de tensión"

    if sm and sm.fragmentation_ratio > 0.5:
        trazo = "alta fragmentación (ratio > 0.5)"
    elif sm and sm.fragmentation_ratio > 0.3:
        trazo = "fragmentación moderada (0.3 < ratio < 0.5)"
    else:
        trazo = "baja fragmentación (ratio < 0.3)"

    grupo = ef.spatial_phenotype.dominant_group if ef else "no determinado"

    resumen = (
        f"Los valores VAD observados indican {intensidad}, {tono}. "
        f"El perfil cromático predominante es {grupo}, y el trazo presenta {trazo}. "
        f"Estos valores son cuantificadores computacionales de características visuales, "
        f"no instrumentos diagnósticos. La interpretación psicológica es responsabilidad "
        f"exclusiva del terapeuta calificado."
    )

    elements.append(Paragraph("Resumen Ejecutivo", styles["Heading2"]))
    elements.append(Paragraph(resumen, estilo_resumen))
    elements.append(Spacer(1, 0.3 * cm))


def _seccion3_perfil_emocional(elements, styles, ef):
    """
    SECCIÓN 3 — Perfil Emocional (VAD) con gráfico de barras y texto clínico.
    Solo se agrega si ef (enriched_features) no es None.
    """
    elements.append(Paragraph("Dimensiones VAD — Valores Cuantitativos", styles["Heading2"]))

    # Gráfico de barras VAD
    chart_vad = build_vad_bar_chart(ef.computational_vad)
    elements.append(DrawingFlowable(chart_vad))
    elements.append(Spacer(1, 0.3 * cm))

    # Texto clínico condicional según los valores
    vad = ef.computational_vad
    textos_clinicos = []

    if vad.valence_estimate > 0.6:
        textos_clinicos.append(GLOSARIO_VAD["valence_high"])
    else:
        textos_clinicos.append(GLOSARIO_VAD["valence_low"])

    if vad.arousal_estimate > 0.5:
        textos_clinicos.append(GLOSARIO_VAD["arousal_high"])
    else:
        textos_clinicos.append(GLOSARIO_VAD["arousal_low"])

    estilo_clinico = ParagraphStyle(
        "clinico",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#444444"),
        spaceAfter=6,
    )
    for texto in textos_clinicos:
        elements.append(Paragraph(f"• {texto}", estilo_clinico))

    elements.append(Spacer(1, 0.5 * cm))


def _seccion4_fenotipado_espacial(elements, styles, ef):
    """
    SECCIÓN 4 — Fenotipado Espacial y Utilization (cuadrantes empíricos).
    Solo se agrega si ef (enriched_features) no es None.
    """
    from app.core.pdi.spatial_analysis import classify_spatial_zone

    elements.append(Paragraph("Fenotipado Espacial y Utilization", styles["Heading2"]))

    centroid = ef.spatial_phenotype.predominant_color_centroid
    zone = classify_spatial_zone(centroid.x_norm, centroid.y_norm)
    qd = ef.spatial_phenotype.quadrant_mass_distribution

    chart_quadrant = build_quadrant_diagram(centroid.x_norm, centroid.y_norm, zone)
    elements.append(DrawingFlowable(chart_quadrant))
    elements.append(Spacer(1, 0.15 * cm))

    estilo_nota_cuadrantes = ParagraphStyle(
        "nota_cuadrantes",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#888888"),
        italic=True,
        spaceAfter=4,
    )
    elements.append(Paragraph(
        "(Etiquetas basadas en el modelo espacial clásico, ver tabla de correlaciones empíricas)",
        estilo_nota_cuadrantes,
    ))
    elements.append(Spacer(1, 0.15 * cm))

    quadrant_data = [
        ["Cuadrante", "Masa %", "Correlación documentada (no diagnóstica)"],
        ["Sup. Izq. (PASADO)", f"{qd.top_left_pct:.0%}", _cell_paragraph("Contenido retrospectivo — correlación documentada (Lange-Küttner 2009)")],
        ["Sup. Der. (FUTURO)", f"{qd.top_right_pct:.0%}", _cell_paragraph("Contenido prospectivo — correlación documentada (Lange-Küttner 2009)")],
        ["Inf. Izq. (MATERIAL)", f"{qd.bottom_left_pct:.0%}", _cell_paragraph("Contenido concreto/corporal — correlación documentada (Lange-Küttner 2009)")],
        ["Inf. Der. (IDEAL)", f"{qd.bottom_right_pct:.0%}", _cell_paragraph("Contenido imaginativo/abstracto — correlación documentada (Lange-Küttner 2009)")],
    ]
    quadrant_table = Table(quadrant_data, colWidths=[5 * cm, 2.5 * cm, 8 * cm])
    quadrant_table.setStyle(_estilo_tabla_base())
    elements.append(quadrant_table)
    elements.append(Spacer(1, 0.3 * cm))

    estilo_clinico = ParagraphStyle(
        "clinico_quadrant",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#444444"),
    )
    texto_zona = GLOSARIO_CUADRANTES.get(zone, "Zona no reconocida en la clasificación espacial.")
    elements.append(Paragraph(f"Zona detectada: <b>{zone}</b> — {texto_zona}", estilo_clinico))

    if ef.canvas_utilization and ef.canvas_utilization.total_used_pct > 0:
        util_pct = ef.canvas_utilization.total_used_pct
        expansion = ef.canvas_utilization.expansion_flag
        elements.append(Paragraph(
            f"Ocupación del canvas: <b>{util_pct:.0%}</b> — Clasificación cuantitativa: <b>{expansion}</b>. "
            f"Este valor mide la proporción de píxeles no blancos sobre el total; la significación clínica "
            f"debe evaluarse en contexto.",
            estilo_clinico,
        ))
    if ef.visual_complexity and ef.visual_complexity.image_entropy > 0:
        elements.append(Paragraph(
            f"Entropía visual: <b>{ef.visual_complexity.image_entropy:.2f}</b> — "
            f"Nivel de organización: <b>{ef.visual_complexity.organization_level}</b>. "
            f"La entropía de Shannon cuantifica la diversidad tonal; la dimensión fractal "
            f"(<b>{ef.visual_complexity.fractal_dimension:.2f}</b>) cuantifica la complejidad estructural. "
            f"Valores descriptivos, no diagnósticos.",
            estilo_clinico,
        ))

    elements.append(Spacer(1, 0.5 * cm))


def _seccion5_trazo(elements, styles, sm):
    """
    SECCIÓN 5 — Características Grafomotoras del Trazo con gráfico espacial y tabla.
    Solo se agrega si sm (stroke_metrics) no es None.
    Todo lenguaje es descriptivo, no concluyente.
    """
    elements.append(
        Paragraph("Características Grafomotoras del Trazo", styles["Heading2"])
    )

    # Gráfico de distribución espacial
    chart_spatial = build_spatial_bar(sm.spatial_distribution)
    elements.append(DrawingFlowable(chart_spatial))
    elements.append(Spacer(1, 0.3 * cm))

    density_interp = (
        f"densidad de bordes elevada ({sm.edge_density_pct:.1%})" if sm.edge_density_pct > 0.15
        else f"densidad de bordes baja ({sm.edge_density_pct:.1%})"
    )

    if sm.mean_edge_intensity > 150:
        intensity_interp = f"intensidad de borde alta ({sm.mean_edge_intensity:.1f})"
    elif sm.mean_edge_intensity > 100:
        intensity_interp = f"intensidad de borde moderada ({sm.mean_edge_intensity:.1f})"
    else:
        intensity_interp = f"intensidad de borde baja ({sm.mean_edge_intensity:.1f})"

    if sm.stroke_continuity > 50:
        continuity_interp = f"longitud media de contorno elevada ({sm.stroke_continuity:.1f} px)"
    else:
        continuity_interp = f"longitud media de contorno corta ({sm.stroke_continuity:.1f} px)"

    if sm.fragmentation_ratio > 0.5:
        frag_texto = GLOSARIO_TRAZO["frag_high"]
    elif sm.fragmentation_ratio > 0.3:
        frag_texto = GLOSARIO_TRAZO["frag_mid"]
    else:
        frag_texto = GLOSARIO_TRAZO["frag_low"]

    stroke_data = [
        ["Métrica", "Valor", "Observación Descriptiva"],
        ["Densidad de bordes", f"{sm.edge_density_pct:.2%}", _cell_paragraph(density_interp)],
        ["Intensidad media", f"{sm.mean_edge_intensity:.1f}", _cell_paragraph(intensity_interp)],
        ["Continuidad", f"{sm.stroke_continuity:.1f} px", _cell_paragraph(continuity_interp)],
        ["Fragmentación", f"{sm.fragmentation_ratio:.2f}", _cell_paragraph(frag_texto)],
        ["Grosor del trazo", f"{sm.edge_thickness_px:.1f}", _cell_paragraph(f"Intensidad promedio de borde: {sm.edge_thickness_px:.1f}")],
        ["Estabilidad grafomotora", f"{sm.graphomotor_stability:.2f}", _cell_paragraph(f"Proporción de contornos continuos (1 − fragmentación): {sm.graphomotor_stability:.2f}")],
    ]
    stroke_table = Table(stroke_data, colWidths=[4 * cm, 3 * cm, 8.5 * cm])
    stroke_table.setStyle(_estilo_tabla_base())
    elements.append(stroke_table)
    elements.append(Spacer(1, 0.5 * cm))


def _seccion6_distribucion_cromatica(elements, styles, color_dist):
    """
    SECCIÓN 6 — Distribución Cromática con torta terapéutica, grupos y colores.
    Solo se agrega si color_dist (color_distribution) no es None.
    """
    elements.append(Paragraph("Distribución Cromática", styles["Heading2"]))

    groups = color_dist.therapeutic_groups

    # Gráfico de torta de grupos terapéuticos
    chart_pie = build_therapeutic_pie(groups)
    elements.append(DrawingFlowable(chart_pie))
    elements.append(Spacer(1, 0.3 * cm))

    # Tabla de grupos terapéuticos
    elements.append(Paragraph("Grupos Terapéuticos", styles["Heading3"]))
    group_data = [
        ["Grupo", "Porcentaje"],
        ["Cálidos (Rojo+Naranja+Amarillo+Tierra)", f"{groups.warm_pct:.2%}"],
        ["Fríos (Verde+Azul+Violeta)", f"{groups.cool_pct:.2%}"],
        ["Neutros (Blanco+Negro+Gris)", f"{groups.neutral_pct:.2%}"],
        ["Otro", f"{groups.other_pct:.2%}"],
    ]
    group_table = Table(group_data, colWidths=[9 * cm, 4 * cm])
    group_table.setStyle(_estilo_tabla_base())
    elements.append(group_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Tabla de colores individuales
    specific = color_dist.specific
    spec_data = [
        ["Color", "Porcentaje"],
        ["Rojo", f"{specific.red_pct:.2%}"],
        ["Naranja", f"{specific.orange_pct:.2%}"],
        ["Amarillo", f"{specific.yellow_pct:.2%}"],
        ["Verde", f"{specific.green_pct:.2%}"],
        ["Azul", f"{specific.blue_pct:.2%}"],
        ["Violeta", f"{specific.violet_pct:.2%}"],
        ["Tonos Tierra", f"{specific.earth_pct:.2%}"],
        ["Blanco", f"{specific.white_pct:.2%}"],
        ["Negro", f"{specific.black_pct:.2%}"],
        ["Gris", f"{specific.gray_pct:.2%}"],
        ["Otro", f"{specific.other_pct:.2%}"],
    ]
    spec_table = Table(spec_data, colWidths=[5 * cm, 5 * cm])
    spec_table.setStyle(_estilo_tabla_base())
    elements.append(spec_table)
    elements.append(Spacer(1, 0.5 * cm))


def _seccion7_anexo_tecnico(elements, styles, s):
    """
    SECCIÓN 7 — Anexo Técnico con histograma HSV y metadatos completos.
    Siempre se agrega al final del reporte.
    """
    elements.append(Paragraph("Anexo Técnico", styles["Heading2"]))

    estilo_nota = ParagraphStyle(
        "nota_tecnica",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.HexColor("#888888"),
        italic=1,
        spaceAfter=8,
    )
    elements.append(Paragraph(
        "Los datos de esta sección son mediciones cuantitativas de características visuales "
        "extraídas por algoritmos de procesamiento digital de imagen. Este sistema no constituye "
        "un instrumento diagnóstico ni psicométrico. Las asociaciones de color (VAD) son heurísticas "
        "computacionales con variabilidad cultural (Cha & Jung 2018). La interpretación psicológica "
        "es responsabilidad exclusiva del terapeuta calificado.",
        estilo_nota,
    ))

    # Picos del histograma HSV si están disponibles
    if s.histogram:
        hist = s.histogram
        if hist.hue and hist.saturation and hist.value:
            hue_peak = max(range(len(hist.hue)), key=lambda i: hist.hue[i])
            sat_peak = max(range(len(hist.saturation)), key=lambda i: hist.saturation[i])
            val_peak = max(range(len(hist.value)), key=lambda i: hist.value[i])
            elements.append(Paragraph(
                f"Histograma HSV — Pico de Tono (H): bin {hue_peak}° | "
                f"Pico de Saturación (S): bin {sat_peak} | "
                f"Pico de Valor (V): bin {val_peak}",
                styles["Normal"],
            ))
            elements.append(Spacer(1, 0.3 * cm))

    # Tabla de metadatos técnicos
    meta_data = [
        ["Campo", "Valor"],
        ["ID de Análisis (completo)", s.analysis_id],
        ["Timestamp", s.timestamp],
    ]
    meta_table = Table(meta_data, colWidths=[5 * cm, 11 * cm])
    meta_table.setStyle(_estilo_tabla_base())
    elements.append(meta_table)


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/reports/{analysis_id}/json")
def get_report_json(analysis_id: str):
    """
    Retorna los datos del análisis PDI en formato JSON.
    Excluye el campo 'images' para aligerar la respuesta.
    """
    s = session.get_session(analysis_id)
    if s is None:
        raise HTTPException(
            status_code=404,
            detail={"error": True, "code": "SESSION_NOT_FOUND"},
        )
    if not session.is_analyzed(analysis_id):
        raise HTTPException(
            status_code=409,
            detail={"error": True, "code": "ANALYSIS_INCOMPLETE"},
        )
    return s.model_dump(exclude={"images"})


@router.get("/reports/{analysis_id}/pdf")
def get_report_pdf(analysis_id: str):
    """
    Genera y retorna el reporte cuantitativo en PDF con 7 secciones descriptivas.
    Incluye gráficos ReportLab embebidos (VAD, cuadrantes espaciales, torta, barras espaciales).
    Todo lenguaje es descriptivo, no diagnóstico. La interpretación clínica es responsabilidad del terapeuta.
    """
    s = session.get_session(analysis_id)
    if s is None:
        raise HTTPException(
            status_code=404,
            detail={"error": True, "code": "SESSION_NOT_FOUND"},
        )
    if not session.is_analyzed(analysis_id):
        raise HTTPException(
            status_code=409,
            detail={"error": True, "code": "ANALYSIS_INCOMPLETE"},
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    # ── Sección 1: Encabezado institucional ─────────────────────────────────
    _seccion1_encabezado(elements, styles, analysis_id, s.timestamp)

    # ── Sección 2: Resumen ejecutivo narrativo ───────────────────────────────
    _seccion2_resumen_ejecutivo(elements, styles, s)

    # ── Sección 3: Perfil emocional VAD ─────────────────────────────────────
    if s.enriched_features:
        _seccion3_perfil_emocional(elements, styles, s.enriched_features)

    # ── Sección 4: Fenotipado espacial ────────────────────────────────────────
    if s.enriched_features:
        _seccion4_fenotipado_espacial(elements, styles, s.enriched_features)

    # ── Sección 5: Dinámica sensoriomotora del trazo ─────────────────────────
    if s.stroke_metrics:
        _seccion5_trazo(elements, styles, s.stroke_metrics)

    # ── Sección 6: Distribución cromática ───────────────────────────────────
    if s.color_distribution:
        _seccion6_distribucion_cromatica(elements, styles, s.color_distribution)

    # ── Sección 7: Anexo técnico ─────────────────────────────────────────────
    _seccion7_anexo_tecnico(elements, styles, s)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="reporte_{analysis_id[:8]}.pdf"'
        },
    )
