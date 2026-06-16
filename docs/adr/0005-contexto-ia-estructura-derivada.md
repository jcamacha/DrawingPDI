# ADR-0005: Contexto IA como Estructura Derivada (AIContext)

**Fecha:** 2026-06-15
**Estado:** APROBADA
**Sprint:** 8 (PDI-27 a PDI-33)

---

## Contexto

Se requiere generar un JSON enriquecido con regiones detectadas, métricas locales, thumbnails y contexto semiótico para que un agente de IA futuro interprete el dibujo proyectivo. El `AnalysisResult` existente solo contiene métricas globales de la imagen completa, sin información por región.

## Problema a Resolver

El pipeline PDI actual produce métricas agregadas de toda la imagen (distribución de color global, VAD global, trazo global). Para que una IA pueda interpretar símbolos individuales dentro del dibujo, necesita:

1. **Regiones detectadas** con coordenadas espaciales (bbox + polígono)
2. **Métricas locales** calculadas solo dentro de cada región
3. **Contexto semiótico** por región (zona Koch, grupo terapéutico, hints de psicología del color)
4. **Relaciones entre regiones** (superposición, proximidad, dirección)
5. **Thumbnails visuales** de cada región para LLMs multimodales

## Opciones Consideradas

### Opción 1: Modificar `AnalysisResult` para incluir regiones

| Pros | Contras |
|------|---------|
| Un solo schema para todo | Rompe compatibilidad con frontend existente |
| Menos código duplicado | Mezcla responsabilidades (métricas globales + regiones) |
| | El frontend recibiría datos que no necesita |

### Opción 2: Crear `AIContext` como estructura separada

| Pros | Contras |
|------|---------|
| Sin impacto en frontend existente | Duplicación parcial de datos |
| Contrato claro y específico para IA | Requiere módulo builder adicional |
| Extensible sin tocar `AnalysisResult` | |
| Endpoint independiente con sus propios errores | |

### Opción 3: Endpoint que combina CV + IA en una sola llamada

| Pros | Contras |
|------|---------|
| Simple para el consumidor | Bloqueante (espera respuesta de LLM) |
| Una sola request | Difícil de testear sin API key |
| | Acoplado al modelo de IA específico |
| | Costoso por cada llamada |

## Decisión

**Opción 2:** `AIContext` como estructura Pydantic separada, generada por un nuevo endpoint `POST /images/{id}/ai-context`.

- La detección de regiones usa **color blobs** (segmentación HSV + `connectedComponentsWithStats`) como fase inicial.
- Soporte futuro para **object detection** (YOLO/GroundingDINO) sin cambiar el schema.
- Los **thumbnails de 224x224** se incluyen como base64 PNG.
- El endpoint requiere que `/analyze` se haya ejecutado primero (HTTP 409 si no).

## Consecuencias

### Nuevos módulos en `core/pdi/`

| Módulo | Función principal |
|--------|-------------------|
| `region_detection.py` | `detect_color_blobs()` — detecta blobs cromáticos con zona semiótica |
| `region_metrics.py` | `compute_region_metrics()` — métricas locales reutilizando funciones core con mask |
| `thumbnails.py` | `generate_region_thumbnail()` — crop 224x224 con padding y base64 |
| `region_relations.py` | `compute_region_relationships()` — superposición, proximidad, dirección, capa |
| `ai_context_builder.py` | `build_ai_context()` — orquestador que ensambla el `AIContext` completo |

### Nuevos modelos Pydantic en `schemas.py`

13 nuevos modelos: `AIMeta`, `AIGlobalClinicalSummary`, `AIBoundingBox`, `AIPolygon`, `AIQuadrantOverlap`, `AIRegionSpatial`, `AIRegionLocalMetrics`, `AIProximityRelation`, `AIRegionRelationships`, `AISemioticHints`, `DetectedRegion`, `AIContext`.

### Nuevo endpoint

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/images/{id}/ai-context` | Genera contexto IA a partir de análisis existente |

### Impacto en tests

39 tests nuevos (26 unitarios + 7 integración + 6 schemas). Total: 98/98 pasando.

### Deuda técnica futura

- Fase 2B: Integrar object detection (YOLO) para etiquetas semánticas reales ("casa", "árbol", "persona")
- Fase 3: Endpoint `POST /ai/interpret` que consume `AIContext` y llama a LLM comercial
- Optimización: NMS (Non-Maximum Suppression) si hay demasiada superposición de blobs
