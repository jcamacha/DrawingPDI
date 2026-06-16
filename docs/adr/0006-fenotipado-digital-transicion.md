# ADR-0006: Transición de Semiótica Psicoanalítica a Fenotipado Digital Empírico

**Estado:** Aceptado  
**Fecha:** 2026-06-15  
**Contexto:** PDI-34 a PDI-41

## Decisión

Reemplazar la terminología psicoanalítica ("semiótico", "masa semiótica", "zones Koch", "psicología del color") con terminología empírica respaldada por literatura ("fenotipado espacial", "perfil cromático", "biomarcadores grafomotores") manteniendo total compatibilidad retroactiva con el frontend existente.

## Cambios Principales

### Nombres de modelos y campos

| Antes (semiótico) | Después (empírico) | Compat retro |
|---|---|---|
| `SemioticMass` | `SpatialPhenotype` | `SemioticMass = SpatialPhenotype` (alias) |
| `AISemioticHints` | `AIEmpiricalHints` | `AISemioticHints = AIEmpiricalHints` (alias) |
| `AIRegionSpatial.semiotic_zone` | `spatial_quadrant` | — |
| `AIRegionSpatial.semiotic_zone_description` | `quadrant_description` | — |
| `DetectedRegion.semiotic_hints` | `empirical_hints` | — |
| `DetectedSymbol.semiotic_zone` | `spatial_quadrant` | — |
| `EnrichedFeatures.semiotic_mass` | `spatial_phenotype` | property alias `semiotic_mass` |

### Constantes y funciones

| Antes | Después |
|---|---|
| `SEMIOTIC_ZONES` | `SPATIAL_QUADRANTS` |
| `classify_semiotic_zone()` | `classify_spatial_zone()` |
| `COLOR_PSYCHOLOGY_HINTS` | `COLOR_EMPIRICAL_HINTS` |
| `THERAPEUTIC_GROUP_MAP` | `CHROMATIC_PROFILE_MAP` |
| `build_koch_diagram()` | `build_quadrant_diagram()` |
| `_seccion4_analisis_semiotico()` | `_seccion4_fenotipado_espacial()` |
| `GLOSARIO_KOCH` | `GLOSARIO_CUADRANTES` |

### Nuevos modelos

- `CanvasUtilization(total_used_pct, expansion_flag, symmetry_index)`
- `VisualComplexity(fractal_dimension, image_entropy, organization_level)`
- `GraphomotorProfile(edge_density_pct, fragmentation_ratio, stroke_continuity, edge_thickness_px, graphomotor_stability)`
- `StrokeMetrics` extendido con `edge_thickness_px` y `graphomotor_stability`

### Nuevos algoritmos

- `compute_canvas_utilization(image)` — porcentaje de utilización del canvas
- `compute_lr_symmetry(image)` — simetría izquierda-derecha
- `compute_visual_entropy(image)` — entropía de Shannon del histograma de grises
- `compute_fractal_dimension(image)` — dimensión fractal por box-counting
- `compute_visual_complexity(image)` — orquestador: entropía + fractal + organización

### Literatura de respaldo

- Garre-Olmo et al. (2017): validación de features grafomotores en DT
- Lange-Küttner (2009): tamaño y ubicación espacial como indicadores evolutivos
- Alwadai & Jaha (2026): proporciones y simetrías en DAP como indicadores cognitivos
- Broadbent et al. (2019): revisión sistemática de dibujo en salud
- Wilms & Oberfeld (2023): modelo VAD computacional por color
- Cha & Jung (2018): variabilidad cultural en asociaciones de color (nota de cautela)

### NOTA sobre VAD_COLOR_WEIGHTS

Documentado como "heurística computacional" explícitamente, no como instrumento psicométrico. Las asociaciones de color están sujetas a variabilidad cultural (Cha & Jung 2018).

### IDs internos

Los IDs de zona (`PASADO`, `FUTURO`, `MATERIAL`, `IDEAL`) se mantienen como constantes internas del sistema. Solo las descripciones e interpretaciones cambiaron de lenguaje psicoanalítico a empírico.

### Pipeline version

`2.0-ai-context` → `3.0-digital-phenotyping`

## Consecuencias

- **Positivas:** Terminología respaldada por literatura empírica; sin claims psicométricos injustificados; disclaimer cultural explícito.
- **Negativas:** Breaking change potencial en consumidores del API (frontend actualizado en el mismo cambio).
- **Riesgo mitigado:** Alias `SemioticMass = SpatialPhenotype` y `AISemioticHints = AIEmpiricalHints` preservan imports existentes; `EnrichedFeatures.semiotic_mass` como property preserva serialización para frontend legacy.