# 2. Imágenes Procesadas como Base64 en JSON de Respuesta

Fecha: 2026-06-09
Estado: Aceptado

## Contexto

El ADR-0001 establece que la subida de imágenes usa `multipart/form-data` (binario crudo) para evitar el overhead del ~33% de Base64. Sin embargo, no toma decisión sobre el formato de **bajada** de las imágenes procesadas (filtrada, Canny, máscara HSV).

El profesor confirma explícitamente: *"El backend responde con un objeto estructurado (JSON) que contiene los porcentajes de color, métricas de trazos y las cadenas de texto en Base64 de las imágenes procesadas."*

Sin esta decisión documentada, un subagente podría implementar respuestas binarias (`image/png`) y el frontend se rompería.

## Opciones consideradas

1. **Imágenes binarias separadas** (`GET /images/{id}/filtered` retorna `image/png`) — Pros: menor tamaño de transferencia. Contras: requiere múltiples requests HTTP, frontend más complejo, no coincide con lo que el profesor especificó.
2. **Base64 embebido en JSON** — Pros: una sola request, frontend simple (`data:image/png;base64,{b64}`), confirmado explícitamente por el profesor. Contras: overhead ~33% en tamaño de transferencia.

## Decisión

Las imágenes procesadas se retornan como strings Base64 dentro del JSON de respuesta del endpoint `POST /api/v1/images/{analysis_id}/analyze`. El campo `images` del modelo `AnalysisResult` contiene `original_b64`, `filtered_b64`, `canny_b64` y `hsv_mask_b64`.

## Consecuencias

- El frontend renderiza imágenes con `<img src="data:image/png;base64,{b64}" />` — simple y directo.
- Una sola llamada HTTP devuelve tanto métricas como imágenes (MVP simple).
- El overhead de Base64 es aceptable para un sistema académico con imágenes de ~1-3MB procesadas.
