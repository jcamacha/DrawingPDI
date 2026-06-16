# Referencia Rápida — Endpoint AI Context

## Endpoint

```
POST /api/v1/images/{analysis_id}/ai-context
```

## Flujo Completo

```bash
# 1. Upload
curl -X POST http://localhost:8000/api/v1/images/upload \
  -F "file=@dibujo.jpg"
# → {"data": {"analysis_id": "abc-123"}, "meta": {...}}

# 2. Analyze
curl -X POST http://localhost:8000/api/v1/images/abc-123/analyze
# → {"data": {AnalysisResult}, "meta": {"elapsed_seconds": 2.34}}

# 3. AI Context
curl -X POST http://localhost:8000/api/v1/images/abc-123/ai-context
# → {"data": {AIContext}, "meta": {"elapsed_seconds": 1.87}}
```

## Respuesta AIContext — Campos Clave

```
AIContext
├── meta
│   ├── analysis_id          # UUID del análisis
│   ├── timestamp            # ISO 8601
│   ├── image_dimensions     # {width, height}
│   └── pipeline_version     # "2.0-ai-context"
│
├── global_context
│   ├── dominant_emotional_tone   # "warm" | "cool" | "neutral"
│   ├── overall_vad               # {valence, arousal, dominance} [0-1]
│   ├── spatial_bias              # "top-left" | "top-right" | "bottom-left" | "bottom-right" | "balanced"
│   ├── fragmentation_level       # "low" | "moderate" | "high"
│   └── total_colored_area_pct    # 0.0 a 1.0
│
├── regions[]                     # Lista de DetectedRegion
│   ├── region_id                 # "reg_001", "reg_002", ...
│   ├── detection_method          # "color_blob" (futuro: "object_detection")
│   ├── label                     # "red_blob", "blue_shape", ...
│   ├── confidence                # 1.0 (determinístico para blobs)
│   │
│   ├── spatial
│   │   ├── bounding_box          # {x, y, width, height}
│   │   ├── polygon               # {points: [[x,y], ...]}
│   │   ├── semiotic_zone         # "PASADO" | "FUTURO" | "MATERIAL" | "IDEAL"
│   │   ├── semiotic_zone_description  # Descripción clínica de la zona
│   │   └── quadrant_overlap      # {top_left_pct, top_right_pct, ...}
│   │
│   ├── local_metrics
│   │   ├── color_distribution    # Mismo schema que global, pero solo del blob
│   │   ├── stroke_metrics        # Mismo schema que global, pero solo del blob
│   │   ├── vad_estimate          # {valence, arousal, dominance} [0-1]
│   │   ├── area_pct_of_canvas    # 0.0 a 1.0
│   │   ├── compactness           # 0.0 a 1.0 (1.0 = círculo perfecto)
│   │   └── dominant_color        # "red" | "blue" | "green" | ...
│   │
│   ├── semiotic_hints
│   │   ├── therapeutic_group     # "warm" | "cool" | "neutral"
│   │   ├── zone_description      # Descripción de zona Koch
│   │   ├── color_psychology_hints# ["red: energy, aggression, ..."]
│   │   └── spatial_interpretation# "Located in the past zone..."
│   │
│   ├── relationships
│   │   ├── overlaps_with         # ["reg_003", ...]
│   │   ├── proximity_to          # [{region_id, distance_px, direction}]
│   │   └── layer_order           # int (basado en coordenada Y)
│   │
│   └── thumbnail_b64             # Base64 PNG 224x224
│
└── interpretation_prompt_template  # String con instrucciones para la IA
```

## Códigos de Error

| HTTP | Code | Significado |
|------|------|-------------|
| 404 | SESSION_NOT_FOUND | El analysis_id no existe |
| 409 | ANALYSIS_INCOMPLETE | Falta ejecutar `/analyze` primero |

## Parámetros Configurables

Se pueden ajustar en `build_ai_context()`:

| Parámetro | Default | Efecto |
|-----------|---------|--------|
| `min_area_pct` | 0.005 | Área mínima del blob (0.5% del canvas) |
| `max_regions` | 30 | Máximo número de regiones retornadas |
