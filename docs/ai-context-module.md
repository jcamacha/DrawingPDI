# Módulo de Contexto IA — Documentación Técnica

**Versión:** 1.0
**Fecha:** 2026-06-15
**Sprint:** 8 (PDI-27 a PDI-33)
**Estado:** Implementado y testeado (98/98 tests)

---

## 1. Propósito

Este módulo genera un JSON enriquecido (`AIContext`) diseñado específicamente para ser consumido por un agente de inteligencia artificial que interprete el significado psicológico de un dibujo proyectivo. El contexto incluye regiones detectadas, métricas locales por región, thumbnails visuales, clasificación semiótica y relaciones espaciales entre elementos.

## 2. Arquitectura

### 2.1 Pipeline de Detección

```
Imagen Original
       │
       ▼
┌─────────────────────────────────┐
│  detect_color_blobs()           │
│  - Segmentación HSV (10 rangos) │
│  - connectedComponentsWithStats │
│  - Filtrado por área mínima     │
│  - Clasificación zona Koch      │
└────────────┬────────────────────┘
             │ Lista de BlobRegion
             ▼
┌─────────────────────────────────┐
│  compute_region_relationships() │
│  - Superposición (bitwise_and)  │
│  - Distancia entre centroides   │
│  - Dirección cardinal (8 dirs)  │
│  - Orden de capa (por Y)        │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌──────────────┐ ┌──────────────────┐
│ Para cada    │ │ build_ai_context │
│ blob:        │ │ (orquestador)    │
│              │ │                  │
│ compute_     │ │ - Global summary │
│ region_      │ │ - Regiones       │
│ metrics()    │ │ - Hints          │
│              │ │ - Prompt template│
│ generate_    │ │                  │
│ thumbnail()  │ │ → AIContext JSON │
└──────────────┘ └──────────────────┘
```

### 2.2 Módulos del Core

| Módulo | Ubicación | Función principal |
|--------|-----------|-------------------|
| `region_detection.py` | `core/pdi/` | Detecta blobs cromáticos usando HSV + connected components |
| `region_metrics.py` | `core/pdi/` | Calcula métricas locales (color, VAD, trazo, compactness) por región |
| `thumbnails.py` | `core/pdi/` | Genera thumbnails 224x224 en base64 para cada región |
| `region_relations.py` | `core/pdi/` | Calcula relaciones espaciales entre regiones |
| `ai_context_builder.py` | `core/pdi/` | Orquestador: ensambla el `AIContext` completo |

### 2.3 Dependencias

- **Reutiliza** funciones core existentes con soporte `mask=`: `compute_color_distribution()`, `compute_color_histogram()`, `compute_vad_from_histogram()`, `compute_stroke_metrics()`
- **Reutiliza** `classify_semiotic_zone()` de `semiotic_config.py`
- **Reutiliza** `apply_canny_edge_detection()` de `edges.py`
- **0 dependencias nuevas** en `requirements.txt`

## 3. Schema JSON — AIContext

### 3.1 Estructura General

```json
{
  "meta": {
    "analysis_id": "uuid-v4",
    "timestamp": "2026-06-15T10:30:00",
    "image_dimensions": {"width": 800, "height": 600},
    "pipeline_version": "2.0-ai-context"
  },
  "global_context": {
    "dominant_emotional_tone": "warm",
    "overall_vad": {
      "valence_estimate": 0.72,
      "arousal_estimate": 0.65,
      "dominance_estimate": 0.40
    },
    "spatial_bias": "top-left",
    "fragmentation_level": "moderate",
    "total_colored_area_pct": 0.45
  },
  "regions": [
    {
      "region_id": "reg_001",
      "detection_method": "color_blob",
      "label": "red_blob",
      "confidence": 1.0,
      "spatial": {
        "bounding_box": {"x": 50, "y": 30, "width": 120, "height": 90},
        "polygon": {"points": [[50,30],[170,30],[170,120],[50,120]]},
        "semiotic_zone": "PASADO",
        "semiotic_zone_description": "Zona del pasado. Elementos vinculados a memoria...",
        "quadrant_overlap": {
          "top_left_pct": 0.75,
          "top_right_pct": 0.25,
          "bottom_left_pct": 0.0,
          "bottom_right_pct": 0.0
        }
      },
      "local_metrics": {
        "color_distribution": {
          "specific": {"red_pct": 0.85, "orange_pct": 0.10, ...},
          "therapeutic_groups": {"warm_pct": 0.95, "cool_pct": 0.0, ...}
        },
        "stroke_metrics": {
          "edge_density_pct": 0.12,
          "mean_edge_intensity": 145.3,
          "stroke_continuity": 42.1,
          "fragmentation_ratio": 0.28,
          "spatial_distribution": {...}
        },
        "vad_estimate": {
          "valence_estimate": 0.80,
          "arousal_estimate": 0.70,
          "dominance_estimate": 0.55
        },
        "area_pct_of_canvas": 0.15,
        "compactness": 0.72,
        "dominant_color": "red"
      },
      "semiotic_hints": {
        "therapeutic_group": "warm",
        "zone_description": "Zona del pasado...",
        "color_psychology_hints": ["red: energy, aggression, vitality, passion, urgency"],
        "spatial_interpretation": "Located in the past zone, may relate to memories..."
      },
      "relationships": {
        "overlaps_with": ["reg_003"],
        "proximity_to": [
          {"region_id": "reg_002", "distance_px": 45.5, "direction": "bottom-right"}
        ],
        "layer_order": 30
      },
      "thumbnail_b64": "iVBORw0KGgoAAAANSUhEUgAA..."
    }
  ],
  "interpretation_prompt_template": "Based on the drawing analysis below..."
}
```

### 3.2 Modelos Pydantic

| Modelo | Campos principales |
|--------|-------------------|
| `AIMeta` | analysis_id, timestamp, image_dimensions, pipeline_version |
| `AIGlobalClinicalSummary` | dominant_emotional_tone, overall_vad, spatial_bias, fragmentation_level, total_colored_area_pct |
| `DetectedRegion` | region_id, detection_method, label, confidence, spatial, local_metrics, semiotic_hints, relationships, thumbnail_b64 |
| `AIRegionSpatial` | bounding_box, polygon, semiotic_zone, semiotic_zone_description, quadrant_overlap |
| `AIRegionLocalMetrics` | color_distribution, stroke_metrics, vad_estimate, area_pct_of_canvas, compactness, dominant_color |
| `AISemioticHints` | therapeutic_group, zone_description, color_psychology_hints, spatial_interpretation |
| `AIRegionRelationships` | overlaps_with, proximity_to, layer_order |
| `AIContext` | meta, global_context, regions, interpretation_prompt_template |

## 4. API

### 4.1 Endpoint

```
POST /api/v1/images/{analysis_id}/ai-context
```

**Precondición:** `POST /api/v1/images/{analysis_id}/analyze` debe haberse ejecutado exitosamente.

**Respuesta exitosa (200):**
```json
{
  "data": { ... AIContext completo ... },
  "meta": {"elapsed_seconds": 2.34}
}
```

**Errores:**

| Código | Detalle | Causa |
|--------|---------|-------|
| 404 | `SESSION_NOT_FOUND` | El analysis_id no existe |
| 409 | `ANALYSIS_INCOMPLETE` | No se ha ejecutado `/analyze` para esta sesión |

### 4.2 Ejemplo de uso con curl

```bash
# 1. Subir imagen
ANALYSIS_ID=$(curl -s -X POST http://localhost:8000/api/v1/images/upload \
  -F "file=@dibujo.jpg" | jq -r '.data.analysis_id')

# 2. Ejecutar análisis PDI
curl -s -X POST http://localhost:8000/api/v1/images/$ANALYSIS_ID/analyze > /dev/null

# 3. Generar contexto IA
curl -s -X POST http://localhost:8000/api/v1/images/$ANALYSIS_ID/ai-context \
  | jq '.data.regions | length'
```

## 5. Algoritmo de Detección de Blobs

### 5.1 Proceso

1. **Segmentación HSV:** Para cada uno de los 10 rangos de color definidos en `COLOR_RANGES_HSV`, se genera una máscara binaria.
2. **Connected Components:** `cv2.connectedComponentsWithStats()` agrupa píxeles conectados en blobs individuales, retornando área y centroide de cada uno.
3. **Filtrado:** Se descartan blobs con área menor al umbral (`min_area_pct`, default 0.5% del canvas).
4. **Geometría:** Para cada blob válido se calcula:
   - Bounding box (`cv2.boundingRect`)
   - Polígono aproximado (`cv2.findContours` + `cv2.approxPolyDP`)
   - Centroide de masa (`cv2.moments`)
5. **Clasificación semiótica:** El centroide normalizado se clasifica en una zona Koch (PASADO/FUTURO/MATERIAL/IDEAL).
6. **Límite:** Máximo `max_regions` blobs (default 30), priorizando los de mayor área.

### 5.2 Parámetros configurables

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `min_area_pct` | 0.005 | Área mínima como fracción del canvas (0.5%) |
| `max_regions` | 30 | Número máximo de regiones a retornar |
| `thumbnail_size` | 224 | Tamaño en píxeles del thumbnail cuadrado |

## 6. Métricas Locales por Región

Cada región recibe las mismas métricas que el análisis global, pero calculadas **solo dentro de su máscara**:

| Métrica | Función core reutilizada |
|---------|--------------------------|
| Distribución de color | `compute_color_distribution(image, mask=blob.mask)` |
| Histograma HSV | `compute_color_histogram(image, mask=blob.mask)` |
| VAD estimado | `compute_vad_from_histogram(histogram, image)` |
| Métricas de trazo | `compute_stroke_metrics(canny_masked)` donde `canny_masked = cv2.bitwise_and(canny, canny, mask=blob.mask)` |
| Compactness | `4π × área / perímetro²` (1.0 = círculo perfecto) |
| Color dominante | Color individual con mayor porcentaje dentro del blob |

## 7. Hints Semióticos

Los hints se generan dinámicamente desde constantes existentes, **no se hardcodean interpretaciones**:

| Hint | Fuente |
|------|--------|
| `therapeutic_group` | Mapeo `THERAPEUTIC_GROUP_MAP` (color_name → warm/cool/neutral) |
| `zone_description` | `SEMIOTIC_ZONES` en `semiotic_config.py` |
| `color_psychology_hints` | `COLOR_PSYCHOLOGY_HINTS` en `ai_context_builder.py` |
| `spatial_interpretation` | Mapeo por zona Koch con interpretación genérica |

## 8. Prompt Template

El `interpretation_prompt_template` incluido en el `AIContext` es un string configurable que estructura la interpretación de la IA:

```
Based on the drawing analysis below, provide a psychological interpretation considering:
1) The global emotional tone and overall spatial distribution patterns.
2) Each detected region's meaning within its semiotic zone (Koch quadrants).
3) The color psychology associations for each region.
4) Relationships between regions (proximity, overlap, layering).
5) Stroke quality metrics (fragmentation, continuity) as indicators of emotional regulation.

Structure your response with:
- A brief executive summary of the overall emotional state.
- Detailed analysis of each significant region.
- Synthesis of spatial patterns and their psychological meaning.
- Observations about relationships between elements.
- Clinical considerations and areas for therapeutic exploration.

IMPORTANT: This is an assistive tool. All interpretations should be validated by a qualified art therapist in the clinical context.
```

**Nota:** El template no incluye referencias bibliográficas. Las interpretaciones se basan en el marco teórico ya presente en los hints semióticos y las métricas.

## 9. Tests

### 9.1 Resumen

| Categoría | Cantidad | Archivos |
|-----------|----------|----------|
| Unitarios | 26 | test_region_detection (6), test_region_metrics (5), test_thumbnails (5), test_region_relations (5), test_ai_context_schemas (5) |
| Integración | 7 | test_ai_context (7) |
| **Total nuevo** | **33** | |
| **Total general** | **98** | (33 nuevos + 65 existentes) |

### 9.2 Casos de prueba clave

| Test | Qué verifica |
|------|-------------|
| `test_detect_single_red_blob` | Detección de un blob rojo simple |
| `test_detect_multiple_color_blobs` | Múltiples blobs de diferentes colores |
| `test_max_regions_limit` | Respeto del límite max_regions |
| `test_region_metrics_circular_blob_compactness` | Compactness ≈ 1.0 para círculo |
| `test_region_metrics_empty_blob_returns_defaults` | Graceful degradation con máscara vacía |
| `test_thumbnail_decodable_as_image` | Thumbnail decodificable a imagen 224x224 |
| `test_two_overlapping_regions` | Detección de superposición entre regiones |
| `test_ai_ctx_full_flow` | Flujo completo upload→analyze→ai-context |
| `test_ai_ctx_regions_have_thumbnails` | Thumbnails válidos en respuesta API |
| `test_ai_ctx_global_context_populated` | Global context con valores en rango |

## 10. Roadmap Futuro

### Fase 2B — Object Detection
- Integrar YOLOv8 o GroundingDINO para detección de objetos reconocibles
- Fusionar resultados: objetos detectados + blobs no cubiertos
- Etiquetas semánticas reales ("casa", "árbol", "persona", "sol")

### Fase 3 — Integración con LLM
- Endpoint `POST /ai/interpret` que consume `AIContext`
- Soporte para múltiples proveedores (OpenAI, Anthropic, Google)
- Cola de trabajos asíncrona para manejar timeouts
- API key configurada en `.env`

### Optimizaciones
- NMS (Non-Maximum Suppression) para blobs superpuestos >70%
- Compresión JPEG para thumbnails si el payload es muy grande
- Caché de `AIContext` para evitar recomputación
