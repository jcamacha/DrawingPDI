# RISK REGISTER — PDI Arteterapia
> Generado: 2026-06-09 | Fuente: AUDITORIA_PLAN_DESARROLLO.md

---

| ID | Riesgo | Categoría | Prob (1-5) | Imp (1-5) | Score | Estrategia | Acción de mitigación |
|----|--------|-----------|------------|-----------|-------|-----------|---------------------|
| R-01 | Sesión en memoria se pierde al reiniciar servidor | Técnico | 4 | 3 | 12 | Aceptar | Documentar limitación en README; MVP académico no requiere persistencia |
| R-02 | Bilateral lento con imágenes >5MP de celular | Técnico | 3 | 4 | 12 | Mitigar | Limitar upload a 10MB; redimensionar a 1920px antes de procesar |
| R-03 | Rojo HSV no detectado por falta de wrap-around | Técnico | 5 | 4 | 20 | Evitar | Implementado con dos rangos (0-10 y 170-180) + test específico (PDI-05) |
| R-04 | CORS bloquea frontend en primer fetch | Técnico | 4 | 5 | 20 | Evitar | CORSMiddleware en main.py como criterio de aceptación (PDI-01) |
| R-05 | Histograma no implementado → RF5 incumplido | Proceso | 3 | 5 | 15 | Evitar | Resuelto en PDI-05 (backend) y PDI-08 (frontend) |
| R-06 | Evaluador penaliza por no usar Gaussiano/Mediana | Proceso | 3 | 4 | 12 | Mitigar | ADR-0003 justifica elección; Gaussiano también implementado (PDI-03) |
| R-07 | RNF3 violado con imágenes grandes (>5s procesamiento) | Técnico | 3 | 3 | 9 | Mitigar | Test de performance en PDI-09; imagen redimensionada antes de procesar |
| R-08 | PDF vacío o ilegible | Técnico | 2 | 3 | 6 | Mitigar | Test de tamaño mínimo en PDI-09; verificación manual |

---

## Detalle de riesgos críticos (Score ≥ 15)

### R-03: Rojo HSV no detectado (Score: 20)
- **Causa raíz:** OpenCV usa H en rango [0, 180], el rojo ocupa 0-10 y 170-180. Usar solo un rango deja ~50% del rojo sin detectar.
- **Mitigación aplicada:** `COLOR_RANGES_HSV` define `red_low` y `red_high`, se combinan con OR binario en `compute_color_distribution`.
- **Test específico:** Imagen artificialmente roja → `specific.red_pct > 0.8`.

### R-04: CORS bloquea frontend (Score: 20)
- **Causa raíz:** Frontend en `:5173`, backend en `:8000` = orígenes distintos. Sin `CORSMiddleware`, el navegador bloquea silenciosamente.
- **Mitigación aplicada:** `CORSMiddleware` con `allow_origins=["http://localhost:5173"]` en `main.py` (PDI-01).
- **Test específico:** Fetch desde frontend al backend sin error de CORS (DoD PDI-01).

### R-05: Histograma ausente → RF5 incumplido (Score: 15)
- **Causa raíz:** El KANBAN original no incluía histograma en ningún ticket. RF5 lo exige explícitamente.
- **Mitigación aplicada:** `compute_color_histogram` en `segmentation.py` (PDI-05) + componente `ColorHistogram` con Recharts (PDI-08).
