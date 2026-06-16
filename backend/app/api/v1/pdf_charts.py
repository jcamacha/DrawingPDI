"""
pdf_charts.py — PDI-24
Módulo de construcción de gráficos ReportLab para el reporte clínico PDF.
Cada función retorna un objeto Drawing listo para ser embebido en un
SimpleDocTemplate mediante la clase DrawingFlowable definida en reports.py.

Todas las primitivas usan reportlab.graphics para garantizar compatibilidad
con la versión reportlab>=4.2.0 ya instalada en el proyecto.
"""

from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Line, Group
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors

from app.core.pdi.schemas import ComputationalVAD, TherapeuticGroups, SpatialDistribution

# ─────────────────────────────────────────────────────────────────────────────
# Colores del sistema de diseño clínico
# ─────────────────────────────────────────────────────────────────────────────
COLOR_VALENCIA = colors.HexColor("#2d6a4f")    # verde oscuro
COLOR_ACTIVACION = colors.HexColor("#f4a261")  # naranja
COLOR_DOMINANCIA = colors.HexColor("#457b9d")  # azul

COLOR_CALIDOS = colors.HexColor("#e63946")     # rojo
COLOR_FRIOS = colors.HexColor("#457b9d")       # azul
COLOR_NEUTROS = colors.HexColor("#adb5bd")     # gris

COLOR_BAR_NO = colors.HexColor("#457b9d")      # azul
COLOR_BAR_NE = colors.HexColor("#2d6a4f")      # verde
COLOR_BAR_SO = colors.HexColor("#f4a261")      # naranja
COLOR_BAR_SE = colors.HexColor("#e63946")      # rojo

# Colores de fondo de los cuadrantes del diagrama de Koch
FONDO_PASADO = colors.HexColor("#f0efeb")
FONDO_FUTURO = colors.HexColor("#e9f5db")
FONDO_MATERIAL = colors.HexColor("#fef9ef")
FONDO_IDEAL = colors.HexColor("#e8f4f8")

# Colores de fondo saturados (cuadrante activo)
FONDO_PASADO_ACTIVO = colors.HexColor("#d6d4c8")
FONDO_FUTURO_ACTIVO = colors.HexColor("#c8e8a4")
FONDO_MATERIAL_ACTIVO = colors.HexColor("#faefd0")
FONDO_IDEAL_ACTIVO = colors.HexColor("#c0e2ef")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN 1 — Gráfico de barras horizontales VAD
# ─────────────────────────────────────────────────────────────────────────────
def build_vad_bar_chart(vad: ComputationalVAD) -> Drawing:
    """
    Construye un HorizontalBarChart con 3 barras (Valencia, Activación, Dominancia).
    Retorna un Drawing de 380×130 px listo para insertar en el PDF.

    Args:
        vad: Objeto ComputationalVAD con los tres estimados normalizados [0, 1].

    Returns:
        Drawing de ReportLab con las barras y leyendas textuales.
    """
    drawing = Drawing(380, 130)

    # Datos: una serie por barra para poder colorear individualmente
    chart = HorizontalBarChart()
    chart.x = 80          # margen izquierdo para etiquetas de categoría
    chart.y = 10
    chart.width = 260
    chart.height = 100
    chart.data = [
        (vad.valence_estimate,),     # serie Valencia
        (vad.arousal_estimate,),     # serie Activación
        (vad.dominance_estimate,),   # serie Dominancia
    ]
    chart.categoryAxis.categoryNames = [""]  # sin etiqueta de categoría

    # Escala del eje numérico
    chart.valueAxis.valueMin = 0.0
    chart.valueAxis.valueMax = 1.0
    chart.valueAxis.valueStep = 0.25

    # Colores individuales por serie
    chart.bars[0].fillColor = COLOR_VALENCIA
    chart.bars[1].fillColor = COLOR_ACTIVACION
    chart.bars[2].fillColor = COLOR_DOMINANCIA

    drawing.add(chart)

    # Leyenda textual a la derecha de cada barra
    # Las barras se distribuyen uniformemente en la altura del chart
    barra_alto = chart.height / 3.0
    etiquetas = [
        (f"Valencia:    {vad.valence_estimate:.2f}", COLOR_VALENCIA),
        (f"Activacion:  {vad.arousal_estimate:.2f}", COLOR_ACTIVACION),
        (f"Dominancia: {vad.dominance_estimate:.2f}", COLOR_DOMINANCIA),
    ]
    for idx, (texto, color) in enumerate(etiquetas):
        # Centrar verticalmente en cada barra (de abajo hacia arriba)
        y_centro = chart.y + (idx + 0.5) * barra_alto
        label = String(chart.x + chart.width + 8, y_centro - 4, texto)
        label.fontName = "Helvetica"
        label.fontSize = 8
        label.fillColor = color
        drawing.add(label)

    return drawing


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN 2 — Gráfico de torta de grupos terapéuticos
# ─────────────────────────────────────────────────────────────────────────────
def build_therapeutic_pie(groups: TherapeuticGroups) -> Drawing:
    """
    Construye un gráfico de torta con 3 sectores (Cálidos, Fríos, Neutros).
    Los sectores con valor 0.0 se omiten para evitar errores en ReportLab.
    Retorna un Drawing de 200×200 px.

    Args:
        groups: Objeto TherapeuticGroups con los porcentajes de cada grupo.

    Returns:
        Drawing de ReportLab con el gráfico de torta.
    """
    drawing = Drawing(200, 200)

    # Construir datos omitiendo sectores con valor cero
    sectores = [
        ("Calidos", groups.warm_pct, COLOR_CALIDOS),
        ("Frios", groups.cool_pct, COLOR_FRIOS),
        ("Neutros", groups.neutral_pct, COLOR_NEUTROS),
    ]
    sectores_validos = [(nombre, valor, color) for nombre, valor, color in sectores if valor > 0.0]

    # Si no hay datos válidos, dibujar un círculo vacío con nota
    if not sectores_validos:
        circulo = Circle(100, 100, 80)
        circulo.fillColor = colors.HexColor("#eeeeee")
        circulo.strokeColor = colors.grey
        drawing.add(circulo)
        nota = String(60, 97, "Sin datos cromaticos")
        nota.fontName = "Helvetica"
        nota.fontSize = 9
        nota.fillColor = colors.grey
        drawing.add(nota)
        return drawing

    pie = Pie()
    pie.x = 30
    pie.y = 30
    pie.width = 140
    pie.height = 140

    pie.data = [v for _, v, _ in sectores_validos]
    pie.labels = [f"{nombre} {valor:.0%}" for nombre, valor, _ in sectores_validos]

    for i, (_, _, color) in enumerate(sectores_validos):
        pie.slices[i].fillColor = color
        pie.slices[i].labelRadius = 1.25
        pie.slices[i].fontSize = 7

    drawing.add(pie)
    return drawing


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN 3 — Diagrama de cuadrantes de Koch
# ─────────────────────────────────────────────────────────────────────────────
def build_quadrant_diagram(centroid_x: float, centroid_y: float, zone: str) -> Drawing:
    """
    Dibuja el diagrama de cuadrantes espaciales usando solo primitivas de ReportLab.
    El rectángulo de la zona activa tiene borde más grueso y fondo más saturado.
    El centroide se marca con un círculo rojo, clampeado al canvas [10, 190].

    Args:
        centroid_x: Coordenada X normalizada [0, 1] del centroide cromático.
        centroid_y: Coordenada Y normalizada [0, 1] del centroide cromático.
        zone: Zona espacial detectada ('PASADO', 'FUTURO', 'MATERIAL', 'IDEAL').

    Returns:
        Drawing de 200×200 px con el diagrama de cuadrantes.
    """
    drawing = Drawing(200, 200)
    tam = 95   # tamaño de cada cuadrante en px
    gap = 10   # separación central en px

    # Definición de cuadrantes: nombre -> (x_orig, y_orig, fondo_normal, fondo_activo, etiqueta)
    # Coordenadas desde esquina inferior-izquierda (ReportLab: Y=0 abajo)
    cuadrantes = {
        "PASADO":   (0,        tam + gap, FONDO_PASADO,   FONDO_PASADO_ACTIVO,   "PASADO"),
        "FUTURO":   (tam + gap, tam + gap, FONDO_FUTURO,  FONDO_FUTURO_ACTIVO,   "FUTURO"),
        "MATERIAL": (0,        0,          FONDO_MATERIAL, FONDO_MATERIAL_ACTIVO, "MATERIAL"),
        "IDEAL":    (tam + gap, 0,         FONDO_IDEAL,    FONDO_IDEAL_ACTIVO,    "IDEAL"),
    }

    for nombre, (ox, oy, fondo_normal, fondo_activo, etiqueta) in cuadrantes.items():
        activo = (nombre == zone)
        rect = Rect(ox, oy, tam, tam)
        rect.fillColor = fondo_activo if activo else fondo_normal
        rect.strokeColor = colors.HexColor("#555555") if activo else colors.HexColor("#aaaaaa")
        rect.strokeWidth = 2 if activo else 0.5
        drawing.add(rect)

        # Etiqueta textual centrada en el cuadrante
        label = String(ox + tam / 2, oy + tam / 2 - 4, etiqueta)
        label.fontName = "Helvetica-Bold" if activo else "Helvetica"
        label.fontSize = 8
        label.fillColor = colors.black
        label.textAnchor = "middle"
        drawing.add(label)

    # Líneas cruzadas en el centro del diagrama
    centro = tam + gap / 2  # 100.0 px
    linea_h = Line(0, centro, 200, centro)
    linea_h.strokeColor = colors.HexColor("#888888")
    linea_h.strokeWidth = 0.5
    drawing.add(linea_h)

    linea_v = Line(centro, 0, centro, 200)
    linea_v.strokeColor = colors.HexColor("#888888")
    linea_v.strokeWidth = 0.5
    drawing.add(linea_v)

    # Posición del centroide en el canvas — invertir Y porque ReportLab tiene Y=0 abajo
    cx = centroid_x * 200
    cy = (1.0 - centroid_y) * 200

    # Clampear para que el círculo no salga del canvas
    cx = max(10.0, min(190.0, cx))
    cy = max(10.0, min(190.0, cy))

    punto = Circle(cx, cy, 6)
    punto.fillColor = colors.red
    punto.strokeColor = colors.darkred
    punto.strokeWidth = 1
    drawing.add(punto)

    return drawing


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN 4 — Barras verticales de distribución espacial
# ─────────────────────────────────────────────────────────────────────────────
def build_spatial_bar(distribution: SpatialDistribution) -> Drawing:
    """
    Construye 4 barras verticales que representan la distribución espacial
    del trazo por cuadrantes (NO, NE, SO, SE).
    Retorna un Drawing de 300×120 px.

    Args:
        distribution: Objeto SpatialDistribution con los porcentajes por cuadrante.

    Returns:
        Drawing de ReportLab con las 4 barras verticales etiquetadas.
    """
    drawing = Drawing(300, 120)

    # Definición de cuadrantes: (etiqueta, valor, color)
    cuadrantes = [
        ("NO", distribution.top_left_pct, COLOR_BAR_NO),
        ("NE", distribution.top_right_pct, COLOR_BAR_NE),
        ("SO", distribution.bottom_left_pct, COLOR_BAR_SO),
        ("SE", distribution.bottom_right_pct, COLOR_BAR_SE),
    ]

    # Área de dibujo con márgenes
    margen_izq = 20
    margen_der = 20
    margen_inf = 25   # espacio para etiquetas inferiores
    margen_sup = 15   # espacio para valores en la punta
    ancho_total = 300 - margen_izq - margen_der
    alto_total = 120 - margen_inf - margen_sup

    # Ancho de barra considerando espacios entre ellas (3 espacios entre 4 barras)
    ancho_barra = ancho_total / 7.0  # 4 barras + 3 espacios iguales
    espacio = ancho_barra

    for idx, (etiqueta, valor, color) in enumerate(cuadrantes):
        # X de inicio de cada barra con espaciado proporcional
        x = margen_izq + idx * (ancho_barra + espacio)
        alto_barra = max(0.0, valor) * alto_total

        # Rectángulo de la barra
        barra = Rect(x, margen_inf, ancho_barra, alto_barra)
        barra.fillColor = color
        barra.strokeColor = colors.transparent
        drawing.add(barra)

        # Etiqueta inferior (nombre del cuadrante)
        label_inf = String(x + ancho_barra / 2, 5, etiqueta)
        label_inf.fontName = "Helvetica-Bold"
        label_inf.fontSize = 9
        label_inf.fillColor = colors.black
        label_inf.textAnchor = "middle"
        drawing.add(label_inf)

        # Valor en la punta superior de la barra
        label_val = String(x + ancho_barra / 2, margen_inf + alto_barra + 2, f"{valor:.0%}")
        label_val.fontName = "Helvetica"
        label_val.fontSize = 8
        label_val.fillColor = colors.HexColor("#333333")
        label_val.textAnchor = "middle"
        drawing.add(label_val)

    # Línea base horizontal
    linea_base = Line(margen_izq, margen_inf, 300 - margen_der, margen_inf)
    linea_base.strokeColor = colors.HexColor("#888888")
    linea_base.strokeWidth = 0.5
    drawing.add(linea_base)

    return drawing
