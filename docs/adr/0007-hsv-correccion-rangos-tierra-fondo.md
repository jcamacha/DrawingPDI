# ADR-0007: Corrección de Clasificación HSV — Rangos, Tierra y Máscara de Fondo

**Estado:** Aceptado  
**Fecha:** 2026-06-15  
**Contexto:** PDI-42 a PDI-47 (bugs identificados en dibujos reales)

## Contexto

Durante pruebas con dibujos reales de arteterapia se identificaron tres bugs críticos en la clasificación de color HSV:

1. **55% clasificado como "otro"** — No existía rango para tonos tierra (marrón/beige/ocre), el color más frecuente en dibujos con pastel.
2. **45-75% clasificado como "blanco"** — El fondo de papel blanco se incluía en el cómputo de color, inflando `neutral_pct` y desplazando los valores VAD hacia neutralidad baja.
3. **Clasificaciones incorrectas por rangos HSV demasiado restrictivos:**
   - Celeste (S≈40) clasificado como blanco (requería S≥100).
   - Verde oscuro (V≈25) clasificado como negro (requería V<50).
   - Rangos superpuestos entre naranja/amarillo/tierra sin resolución de prioridad.

Además, el balance de blancos automático (Gray-World) destruía imágenes de color sólido sin fondo blanco, distorsionando los resultados.

## Decisión

Implementar cinco correcciones coordinadas en `segmentation.py` y modelos asociados:

### 1. Máscara de contenido (`_compute_content_mask`)

Umbral gray>240 con cierre morfológico para excluir el papel blanco del análisis cromático. Solo los píxeles del contenido dibujado se contabilizan para distribución de color, histograma HSV y VAD.

```python
_WHITE_BG_THRESHOLD = 240
_MORPH_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

def _compute_content_mask(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, _MORPH_KERNEL)
    return mask
```

### 2. Balance de blancos condicional (`auto_white_balance`)

El balance de blancos Gray-World solo se aplica cuando ≥15% del fondo es blanco (`_has_significant_background`). En imágenes de color sólido (tests unitarios, dibujos sin fondo), se omite para no distorsionar los colores.

```python
def _has_significant_background(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    white_pixels = float(np.count_nonzero(gray >= 240))
    total = float(image.shape[0] * image.shape[1])
    return (white_pixels / total) >= 0.15
```

Condición aplicada en `compute_color_distribution`, `compute_color_histogram`, `compute_chromatic_mass` y `generate_hsv_mask_visualization`.

### 3. Rangos HSV corregidos

| Color | Antes (H, S, V) | Después (H, S, V) | Razón |
|-------|------------------|---------------------|--------|
| Blanco | S<30, V>200 | S<15, V>200 | Evitar celeste (S≈40) clasificado como blanco |
| Negro | V<50 | V<30 | Evitar verde oscuro (V≈35) clasificado como negro |
| Azul | S≥100, V≥100 | S≥40, V≥40 | Capturar celeste y azul pastel |
| Amarillo | S≥100, V≥100 | S≥40, V≥70 | Capturar amarillo pastel |
| Naranja | H=8-25, S≥50, V≥70 | H=8-25, S≥50, V≥70 | Sin cambio |
| **Tierra** | — | H=8-25, S=30-180, V=40-180 | **NUEVO**: marrón, beige, ocre |

### 4. Clasificación por prioridad (`_COLOR_PRIORITY`)

Los rangos de naranja/amarillo/tierra se superponen en H=8-25. Se establece un orden de prioridad estricto: blanco → negro → gris → rojo → violeta → azul → verde → amarillo → naranja → tierra. Cada píxel se asigna al primer rango que cumpla, evitando doble conteo.

```python
_COLOR_PRIORITY = [
    "white", "black", "gray",
    "red_low", "red_high", "violet", "blue", "green",
    "yellow", "orange", "earth",
]
```

Naranja (S≥50) tiene prioridad sobre tierra (S≥30). La tierra captura los tonos desaturados (S=30-50) que antes caían en "otro".

### 5. Modelo `SpecificColors` extendido con `earth_pct`

```python
class SpecificColors(BaseModel):
    red_pct: float = 0.0
    orange_pct: float = 0.0
    yellow_pct: float = 0.0
    green_pct: float = 0.0
    blue_pct: float = 0.0
    violet_pct: float = 0.0
    earth_pct: float = 0.0  # NUEVO
    white_pct: float = 0.0
    black_pct: float = 0.0
    gray_pct: float = 0.0
    other_pct: float = 0.0
```

La categoría "tierra" se clasifica como **cálida** en grupos terapéuticos (asociación grounding/corporal). Default 0.0 para retrocompatibilidad.

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `backend/app/core/pdi/segmentation.py` | Rangos HSV corregidos, `_compute_content_mask()`, `auto_white_balance()`, `_has_significant_background()`, `_COLOR_PRIORITY`, mimetype mask exclusivo por prioridad |
| `backend/app/core/pdi/schemas.py` | `earth_pct` en `SpecificColors` |
| `backend/app/core/pdi/ai_context_builder.py` | `COLOR_EMPIRICAL_HINTS["earth"]`, `CHROMATIC_PROFILE_MAP["earth"]="warm"`, `VAD_COLOR_WEIGHTS["earth"]` |
| `backend/app/api/v1/reports.py` | Fila "Tonos Tierra" en tabla de colores, label "Cálidos (Rojo+Naranja+Amarillo+Tierra)" |
| `backend/app/api/v1/pdf_charts.py` | Sin cambios (la torta usa grupos terapéuticos, no colores individuales) |
| `frontend/src/components/MetricsPanel.jsx` | `earth_pct` con label "Tonos Tierra" y color sienna `#a0522d` |

## Tests

De 6 tests originales a 23 tests en `test_segmentation.py`:

| Test | Propósito |
|------|-----------|
| `test_distribution_has_required_keys` | Estructura de respuesta |
| `test_specific_sums_approx_one` | Suma ≈ 1.0 |
| `test_therapeutic_groups_sums_approx_one` | Suma ≈ 1.0 |
| `test_red_image_warm_high` | Imagen roja sin fondo → warm |
| `test_blue_image_cool_high` | Imagen azul → cool |
| `test_histogram_correct_lengths` | Longitudes H/S/V |
| `test_earth_color_classified` | HSV(H=18,S=36,V=90) → earth_pct > 0.1 |
| `test_blue_celeste_not_white` | HSV(H=105,S=40,V=200) → blue, no white |
| `test_dark_green_not_black` | HSV(H=60,S=80,V=35) → green > black |
| `test_white_background_excluded` | Fondo blanco 75% → no inflar neutral |
| `test_content_mask_excludes_white_background` | bg=245 → mask < 10% del canvas |
| `test_auto_white_balance` | Gray-World: canales convergen al promedio |
| `test_distribution_with_explicit_mask` | Masks explícitos |
| `test_distribution_empty_mask_returns_zeros` | Mask vacía → todo ceros |
| `test_priority_no_double_counting` | Superposición H=10,S=120,V=150 → orange+earth ≤ 1.01 |
| `test_specific_keys_include_earth` | earth_pct existe en respuesta |
| `test_canvas_utilization` | Utilización y flag de expansión |
| `test_lr_symmetry` | Simetría I-D |
| `test_visual_entropy` | Entropía de Shannon > 0 |
| `test_fractal_dimension` | Dimensión fractal ≥ 0 |
| `test_visual_complexity` | Keys y organization_level |
| `test_vad_from_histogram_with_image` | VAD con color |
| `test_chromatic_mass` | Centroide y distribución por cuadrantes |

Resultado: **110/115 tests pasan** (5 fallos pre-existentes por archivo fixture faltante, no relacionados).

## Consecuencias

- **Positivas:** Eliminación de los 3 bugs críticos (55% "otro" → tierra, fondo blanco excluido, clasificaciones correctas de celeste y verde oscuro). Retrocompatibilidad preservada vía `earth_pct: float = 0.0`.
- **Negativas:** El porcentaje de "otro" puede seguir siendo >0 para colores fuera de los 10 rangos definidos (ej. magenta puro, cian de alta saturación). La máscara de contenido puede excluir regiones muy claras del dibujo que se confundan con fondo.
- **Riesgo mitigado:** Tests unitarios con imágenes sintéticas HSV cubren los 3 bugs originales. La clasificación por prioridad elimina doble conteo. AWB condicional no distorsiona imágenes sin fondo blanco.

## Alternativas Consideradas

1. **Umbral de fondo binario fijo sin morfología** — Más simple, pero deja gaps en trazos finos donde el fondo "se filtra" entre píxeles de stroke. Se eligió cierre morfológico (kernel 3×3) para mitigar.
2. **AWB incondicional** — Destruye imágenes de color sólido (caso de tests y dibujos sin fondo). Se eligió AWB condicional (≥15% fondo blanco).
3. **Earth como sub-rango de naranja** — Imposible porque la distinción es la baja saturación (S=30-50 vs S≥50 para naranja). Se requiere rango separado con resolución de prioridad.
4. **K-means para clasificación** — Correcto teóricamente, pero no determinista y difícil de reproducir entre ejecuciones. Se eligieron rangos HSV explícitos con prioridad.
5. **Umbral de fondo adaptativo (Otsu)** — Otsu no distingue bien cuando la imagen tiene >50% de fondo blanco uniforme. Se eligió umbral fijo (gray>240) por robustez en el caso de uso dominante (papel blanco).