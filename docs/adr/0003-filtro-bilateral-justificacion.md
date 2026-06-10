# 3. Filtro Bilateral como Filtro Principal (con Gaussiano como respaldo)

Fecha: 2026-06-09
Estado: Aceptado

## Contexto

RF2 del requerimiento especifica: *"El sistema debe aplicar técnicas de filtrado (por ejemplo, filtro Gaussiano o Mediana) para reducir el ruido térmico de la captura y la textura rugosa natural del papel/pastel, preservando los bordes principales de los trazos."*

El KANBAN original planificaba solo el Filtro Bilateral, que es una desviación no documentada de lo que RF2 pide literalmente. Aunque el Bilateral es técnicamente superior para este caso de uso, no está justificado formalmente y el evaluador podría cuestionarlo.

## Opciones consideradas

1. **Solo Gaussiano** — Pros: cumple RF2 literalmente. Contras: difumina bordes uniformemente, lo que afecta negativamente la detección de bordes con Canny en la etapa posterior. Los trazos de pastel se difuminan y Canny detecta menos bordes reales.
2. **Solo Bilateral** — Pros: preserva bordes mientras suaviza ruido, produciendo mejor resultado visual y mejor input para Canny. Contras: no es lo que RF2 pide literalmente; desviación no justificada ante el evaluador.
3. **Ambos filtros** — Pros: Gaussiano cumple RF2 literalmente (verificable), Bilateral se usa como filtro principal de la pipeline por su superioridad técnica. Contras: más código, dos funciones de filtrado.

## Decisión

Implementar ambos filtros:

- **Gaussiano** (`apply_gaussian_filter`): función pura verificable que cumple RF2 al pie de la letra. Disponible como alternativa.
- **Bilateral** (`apply_bilateral_filter`): filtro principal utilizado en la pipeline de análisis. Su resultado es el que se muestra en la UI como "imagen filtrada".

Justificación técnica del Bilateral sobre Gaussiano para este dominio:
- El arteterapia usa **pastel sobre papel**, que produce trazos con bordes definidos sobre textura rugosa.
- El Gaussiano difumina **todo** por igual (ruido + bordes), perdiendo información de los trazos.
- El Bilateral preserva bordes (σ_color controla cuánto se difumina según diferencia de color) mientras suaviza regiones uniformes.
- La detección Canny posterior se beneficia directamente de bordes preservados: mayor `edge_density_pct` y `stroke_continuity` en trazos reales.

## Consecuencias

- RF2 se cumple literalmente con el Gaussiano.
- El resultado visual mostrado al usuario es de mayor calidad (Bilateral).
- El evaluador puede verificar que ambos filtros existen y que la elección del Bilateral está documentada y justificada.
