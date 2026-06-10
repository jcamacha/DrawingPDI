"""
reports.py — PDI-25
Endpoints de generación de reportes clínicos PDF y JSON para Arteterapia.
Refactorización completa con 7 secciones narrativas y gráficos ReportLab.

Endpoints disponibles:
    GET /reports/{analysis_id}/json  — Datos de análisis en formato JSON
    GET /reports/{analysis_id}/pdf   — Reporte clínico en PDF con gráficos
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
    build_koch_diagram,
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
# Glosarios clínicos para interpretación narrativa
# ─────────────────────────────────────────────────────────────────────────────
GLOSARIO_VAD = {
    "valence_high": (
        "El paciente presenta una tendencia hacia estados emocionales positivos o de bienestar. "
        "Los colores predominantes se asocian a experiencias agradables."
    ),
    "valence_low": (
        "Los colores predominantes se asocian con estados de mayor tensión emocional "
        "o introversión afectiva."
    ),
    "arousal_high": (
        "La paleta cromática sugiere un estado de alta activación o energía emocional "
        "durante la sesión."
    ),
    "arousal_low": (
        "El uso cromático indica un estado de calma, ensimismamiento o baja energía expresiva."
    ),
}

GLOSARIO_KOCH = {
    "PASADO": (
        "La concentración de masa en el cuadrante izquierdo puede vincularse con experiencias "
        "pasadas, vínculos afectivos tempranos o pensamiento retrospectivo."
    ),
    "FUTURO": (
        "La masa cromática se proyecta hacia el lado derecho, asociado con expectativas, "
        "planificación o proyección al futuro."
    ),
    "MATERIAL": (
        "La concentración en la zona inferior sugiere anclaje en lo concreto, lo corporal "
        "y las necesidades básicas."
    ),
    "IDEAL": (
        "La distribución en la zona superior se vincula con la espiritualidad, la imaginación "
        "y los ideales."
    ),
}

GLOSARIO_TRAZO = {
    "frag_high": (
        "El trazo muestra alta fragmentación: los gestos expresivos son cortos e interrumpidos, "
        "lo que puede reflejar ansiedad motriz, duda o exploración cautelosa."
    ),
    "frag_mid": (
        "La fragmentación moderada indica un balance entre impulso expresivo y control "
        "consciente del gesto."
    ),
    "frag_low": (
        "El trazo es fluido y continuo, indicando expresión espontánea y confianza en el gesto."
    ),
}


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
    ])


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

    elements.append(Paragraph("Reporte Clínico de Arteterapia — Análisis PDI", styles["Title"]))
    elements.append(Paragraph(
        "Procesamiento Digital de Imágenes aplicado a la evaluación de la producción artística",
        estilo_subtitulo,
    ))

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
    SECCIÓN 2 — Resumen ejecutivo en lenguaje natural (sin números brutos).
    Genera un párrafo narrativo basado en los estimados VAD y métricas de trazo.
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

    # Determinar intensidad emocional según arousal
    if ef and ef.computational_vad.arousal_estimate > 0.6:
        intensidad = "alta activación emocional"
    elif ef and ef.computational_vad.arousal_estimate > 0.4:
        intensidad = "activación emocional moderada"
    else:
        intensidad = "baja activación emocional"

    # Determinar tono según valencia
    if ef and ef.computational_vad.valence_estimate > 0.6:
        tono = "predominantemente positivo"
    elif ef and ef.computational_vad.valence_estimate > 0.4:
        tono = "de tono neutro"
    else:
        tono = "de carga emocional intensa"

    # Determinar calidad del trazo según fragmentación
    if sm and sm.fragmentation_ratio > 0.5:
        trazo = "fragmentado e interrumpido"
    elif sm and sm.fragmentation_ratio > 0.3:
        trazo = "moderadamente fragmentado"
    else:
        trazo = "fluido y continuo"

    # Grupo cromático dominante
    grupo = ef.semiotic_mass.dominant_group if ef else "no determinado"

    resumen = (
        f"La producción artística analizada presenta {intensidad} con un tono {tono}. "
        f"El grupo cromático predominante es {grupo}, y el trazo es {trazo}. "
        f"Se recomienda al terapeuta complementar este análisis cuantitativo con la "
        f"observación clínica directa del proceso creativo."
    )

    elements.append(Paragraph("Resumen Ejecutivo", styles["Heading2"]))
    elements.append(Paragraph(resumen, estilo_resumen))
    elements.append(Spacer(1, 0.3 * cm))


def _seccion3_perfil_emocional(elements, styles, ef):
    """
    SECCIÓN 3 — Perfil Emocional (VAD) con gráfico de barras y texto clínico.
    Solo se agrega si ef (enriched_features) no es None.
    """
    elements.append(Paragraph("Perfil Emocional — Dimensiones VAD", styles["Heading2"]))

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


def _seccion4_analisis_semiotico(elements, styles, ef):
    """
    SECCIÓN 4 — Análisis Semiótico y Espacial (Test de Koch).
    Solo se agrega si ef (enriched_features) no es None.
    """
    from app.core.pdi.semiotic_config import classify_semiotic_zone

    elements.append(Paragraph("Análisis Semiótico y Espacial (Test de Koch)", styles["Heading2"]))

    # Calcular zona y centroide
    centroid = ef.semiotic_mass.predominant_color_centroid
    zone = classify_semiotic_zone(centroid.x_norm, centroid.y_norm)
    qd = ef.semiotic_mass.quadrant_mass_distribution

    # Diagrama de Koch
    chart_koch = build_koch_diagram(centroid.x_norm, centroid.y_norm, zone)
    elements.append(DrawingFlowable(chart_koch))
    elements.append(Spacer(1, 0.3 * cm))

    # Tabla de distribución de masa por cuadrantes con interpretación clínica
    koch_data = [
        ["Cuadrante", "Masa", "Interpretación Clínica"],
        ["Superior Izq. (PASADO)", f"{qd.top_left_pct:.0%}", "Vínculo con experiencias pasadas"],
        ["Superior Der. (FUTURO)", f"{qd.top_right_pct:.0%}", "Proyección y expectativas"],
        ["Inferior Izq. (MATERIAL)", f"{qd.bottom_left_pct:.0%}", "Anclaje en lo concreto"],
        ["Inferior Der. (IDEAL)", f"{qd.bottom_right_pct:.0%}", "Aspiraciones e idealización"],
    ]
    koch_table = Table(koch_data, colWidths=[5 * cm, 2.5 * cm, 8 * cm])
    koch_table.setStyle(_estilo_tabla_base())
    elements.append(koch_table)
    elements.append(Spacer(1, 0.3 * cm))

    # Texto clínico de la zona detectada
    estilo_clinico = ParagraphStyle(
        "clinico_koch",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#444444"),
    )
    texto_zona = GLOSARIO_KOCH.get(zone, "Zona no reconocida en la clasificación semiótica.")
    elements.append(Paragraph(f"Zona detectada: <b>{zone}</b> — {texto_zona}", estilo_clinico))
    elements.append(Spacer(1, 0.5 * cm))


def _seccion5_trazo(elements, styles, sm):
    """
    SECCIÓN 5 — Dinámica Sensoriomotora del Trazo con gráfico espacial y tabla.
    Solo se agrega si sm (stroke_metrics) no es None.
    """
    elements.append(
        Paragraph("Calidad del Trazo y Dinámica Sensoriomotora", styles["Heading2"])
    )

    # Gráfico de distribución espacial
    chart_spatial = build_spatial_bar(sm.spatial_distribution)
    elements.append(DrawingFlowable(chart_spatial))
    elements.append(Spacer(1, 0.3 * cm))

    # Determinar interpretación de densidad
    density_interp = (
        "trazos enérgicos/densos" if sm.edge_density_pct > 0.15 else "trazos suaves/dispersos"
    )

    # Determinar interpretación de intensidad
    if sm.mean_edge_intensity > 150:
        intensity_interp = "Alta presión del trazo"
    elif sm.mean_edge_intensity > 100:
        intensity_interp = "Presión moderada"
    else:
        intensity_interp = "Trazo ligero o sin presión"

    # Determinar interpretación de continuidad
    continuity_interp = (
        "Trazos amplios y fluidos" if sm.stroke_continuity > 50
        else "Trazos cortos y exploratorios"
    )

    # Determinar texto de fragmentación
    if sm.fragmentation_ratio > 0.5:
        frag_texto = GLOSARIO_TRAZO["frag_high"]
    elif sm.fragmentation_ratio > 0.3:
        frag_texto = GLOSARIO_TRAZO["frag_mid"]
    else:
        frag_texto = GLOSARIO_TRAZO["frag_low"]

    stroke_data = [
        ["Métrica", "Valor", "Significado Clínico"],
        ["Densidad de bordes", f"{sm.edge_density_pct:.2%}", density_interp],
        ["Intensidad media", f"{sm.mean_edge_intensity:.1f}", intensity_interp],
        ["Continuidad", f"{sm.stroke_continuity:.1f} px", continuity_interp],
        ["Fragmentación", f"{sm.fragmentation_ratio:.2f}", frag_texto],
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
        ["Cálidos (Rojo+Naranja+Amarillo)", f"{groups.warm_pct:.2%}"],
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
        "Los datos de esta sección son para uso técnico y académico. "
        "No se recomienda su interpretación clínica directa sin el contexto del sistema completo.",
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
    Genera y retorna el reporte clínico en PDF con 7 secciones narrativas.
    Incluye gráficos ReportLab embebidos (VAD, Koch, torta, barras espaciales).
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

    # ── Sección 4: Análisis semiótico Koch ───────────────────────────────────
    if s.enriched_features:
        _seccion4_analisis_semiotico(elements, styles, s.enriched_features)

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
