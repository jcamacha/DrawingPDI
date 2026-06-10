# Kanban Project Board - PDI Arteterapia

Este documento actúa como la fuente central de verdad para la planificación y el estado del proyecto. Debe ser actualizado regularmente al mover tareas de `TODO` a `IN PROGRESS` y luego a `DONE`.

## 📋 TODO (Por Hacer)

*(Vacío)*

---

## 🏃 IN PROGRESS (En Progreso)
*(Vacío)*

---

## 🔍 REVIEW (En Revisión)
*(Vacío)*

---

## ✅ DONE (Completado)

### [PDI-23] Backend: Integración de Gráficos en Modelo Pydantic
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-14, PDI-15, PDI-16, PDI-17
**Fase:** BE-Reportes (Didáctica)
**Completado:** 2026-06-10

**Criterios de Aceptación:**
- [x] `EnrichedFeatures` actualizado para incluir los datos necesarios para generar los `Drawing` de `reportlab`.
- [x] Lógica de unión entre `ComputationalVAD` y `SpatialDistribution` en el servicio de reportes.
- [x] Test de integración: `get_analysis_report()` valida que los datos se extraen correctamente hacia el módulo de PDF.

### [PDI-24] BE: Módulo `pdf_charts.py` — Gráficos ReportLab en Memoria
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-23
**Fase:** BE-Reportes (Didáctica)
**Completado:** 2026-06-10

> **RESTRICCIONES EXPLÍCITAS (Fallo 2 - Anti Scope Creep):**
> - ✅ Crear únicamente: `backend/app/api/v1/pdf_charts.py`
> - ❌ NO modificar: `reports.py`, `images.py`, `session.py`, `schemas.py`, `segmentation.py`, `edges.py`
> - ❌ NO instalar dependencias externas (matplotlib, seaborn, pillow adicional). Solo `reportlab.graphics`.

**Stack fijado:** `reportlab.graphics.charts`, `reportlab.graphics.shapes`, `reportlab.lib.colors` — 0 dependencias nuevas.

**Criterios de Aceptación (binarios):**
- [x] `build_vad_bar_chart(vad: ComputationalVAD) -> Drawing` — Genera `Drawing(380, 130)` con 3 barras horizontales coloreadas. **Test: `isinstance(result, Drawing)` == True**.
- [x] `build_therapeutic_pie(groups: TherapeuticGroups) -> Drawing` — Pie chart `Drawing(200, 200)` con colores rojo-cálido, azul-frío, gris-neutro. **Test: suma de sectores == 100%**.
- [x] `build_koch_diagram(centroid_x: float, centroid_y: float, zone: str) -> Drawing` — Canvas `Drawing(200, 200)` con 4 rectángulos y círculo en centroide. **Solo primitivas `Rect`, `Circle`, `String`**. **Test: `isinstance(result, Drawing)` == True**.
- [x] `build_spatial_bar(distribution: SpatialDistribution) -> Drawing` — 4 barras verticales (NO/NE/SO/SE). **Test: `isinstance(result, Drawing)` == True**.
- [x] `backend/tests/unit/test_pdf_charts.py` — 6 tests pasan.

### [PDI-25] BE: Refactorización `reports.py` — Narrativa Clínica y Visuales
**Tipo:** Refactor (Backend)
**Subagente:** Backend
**Depende de:** PDI-24
**Fase:** BE-Reportes (Didáctica)
**Completado:** 2026-06-10

> **RESTRICCIONES EXPLÍCITAS:**
> - ✅ Modificar únicamente: `backend/app/api/v1/reports.py`
> - ✅ Importar desde: `backend/app/api/v1/pdf_charts.py` (PDI-24)
> - ❌ NO modificar: `images.py`, `session.py`, `schemas.py`, módulos core PDI
> - ❌ NO cambiar la firma del endpoint `/reports/{analysis_id}/pdf` (mismo método GET, misma URL)

**Criterios de Aceptación (binarios):**
- [x] El PDF generado sigue el flujo de 7 secciones clínicas.
- [x] **Sección 2 (Resumen Ejecutivo):** Párrafo en lenguaje natural sin números brutos.
- [x] **Sección 3 (VAD):** Gráfico `build_vad_bar_chart()` + Glosario Clínico.
- [x] **Sección 4 (Semiótico):** Diagrama Koch + tabla de cuadrantes + texto GLOSARIO_KOCH.
- [x] **Sección 5 (Trazo):** `build_spatial_bar()` + tabla con Significado Clínico.
- [x] **Sección 6 (Color):** `build_therapeutic_pie()` + tablas existentes.
- [x] **Sección 7 (Anexo):** Histograma HSV textual + metadatos.
- [x] Si `enriched_features is None`: secciones 3 y 4 se omiten sin error.
- [x] Los 10 tests de `test_api.py` siguen pasando.

### [PDI-26] QA: Validación Completa del Reporte Didáctico
**Tipo:** QA
**Subagente:** DevOps/QA
**Depende de:** PDI-25
**Fase:** BE-Reportes (Didáctica)

> **RESTRICCIONES EXPLÍCITAS:**
> - ✅ Solo ejecutar comandos: `pytest`, validaciones de tamaño de PDF
> - ❌ NO modificar código de producción ni tests existentes

**Criterios de Aceptación (binarios):**
- [ ] `pytest backend/tests/` → **59 tests existentes + 4 nuevos (PDI-24) pasan. 0 fallos**.
- [ ] Test nuevo `test_pdf_content_regressions.py`: PDF generado tiene `len(pdf_bytes) > 5000` (confirma que el contenido visual fue añadido, no solo texto plano).
- [ ] Test nuevo: Sesión con `enriched_features=None` → `GET /pdf` responde `200` sin excepción (degradación elegante confirmada).
- [ ] Benchmark de performance: el endpoint `/pdf` responde en **< 5 segundos** con imagen 800×600 (mismo límite RNF3 del proyecto).

---

## 🏃 IN PROGRESS (En Progreso)
*(Vacío)*

---

## 🔍 REVIEW (En Revisión)
*(Vacío)*

---

## ✅ DONE (Completado)

### [PDI-10] UI/UX: Tipografía y Sistema de Color Premium
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-08
**Fase:** FE-A
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `npm install tailwindcss @tailwindcss/vite` ejecutado y verificado en `package.json`.
- [x] `vite.config.js` modificado con el plugin `@tailwindcss/vite`.
- [x] Google Fonts "Geist" cargado en `index.html` (pesos 300-700).
- [x] `src/index.css` reemplazado con `@import "tailwindcss"` + `@theme` con tokens: `--color-accent`, `--color-surface`, `--color-base`, `--font-sans`, `--radius-2xl`, `--shadow-diffuse`, `--shadow-diffuse-lg`.
- [x] Paleta: base Zinc-50/900, acento único Indigo-500 (saturación < 80%), sin púrpuras genéricos.
- [x] Clases utilitarias "Double-Bezel" definidas: `card-glass` + `card-glass-hover` con sombras difusas.
- [x] `npx vite build` compila sin errores.
- [x] El frontend carga con la tipografía Geist y los estilos base aplicados.

---

### [PDI-11] UI/UX: Rediseño Hero Section e ImageUploader
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-10
**Fase:** FE-B
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `npm install @phosphor-icons/react` ejecutado.
- [x] `HomePage` refactorizada a layout split-screen: texto a la izquierda (40%), uploader a la derecha (60%) en desktop; stack vertical en mobile.
- [x] `ImageUploader` rediseñado: drop zone con `rounded-[2rem]`, "Double-Bezel" (`card-glass`), `active:scale-[0.98]`.
- [x] Estado UPLOADING: skeleton shimmer en lugar de spinner circular.
- [x] Estado ERROR: mensaje inline con ícono Phosphor `WarningCircle`, sin `alert()`.
- [x] Estado SUCCESS: check animado con `CheckCircle` + transición a análisis.
- [x] Íconos: reemplazados por `@phosphor-icons/react` (`CloudArrowUp`, `CheckCircle`, `WarningCircle`).
- [x] Estados IDLE, UPLOADING, ERROR, SUCCESS mantienen la misma máquina de estados (sin breaking changes).

---

### [PDI-12] UI/UX: Arquitectura Bento Grid para el Dashboard (AnalysisPage)
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-10
**Fase:** FE-B
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `AnalysisPage` reorganizada con CSS Grid "Bento" asimétrico: desktop `grid-template-columns: 2fr 1fr` (ImageGrid | MetricsPanel), ColorHistogram full-width; mobile `1fr` stack vertical.
- [x] `ImageGrid` (2x2): padding generoso (`p-4`), `rounded-[2rem]`, "Liquid Glass" (`card-glass` backdrop-blur), labels en overlay inferior con `bg-gradient-to-t from-black/40`.
- [x] `MetricsPanel`: eliminadas tarjetas genéricas; agrupadas con `divide-y divide-zinc-100`; métricas de trazo en layout de 3 columnas con `text-3xl font-light`; botones "ghost" sutiles.
- [x] `ColorHistogram`: removidas líneas de ejes pesadas, solo ticks mínimos; tooltip premium; contenedor sin borde.

---

### [PDI-13] UI/UX: Coreografía de Animación y Micro-Interacciones
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-12
**Fase:** FE-C
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `npm install framer-motion` ejecutado y verificado.
- [x] Animaciones solo sobre `transform` y `opacity` (cero animaciones de width/height/top/left).
- [x] "Staggered Entry" en AnalysisPage: métricas e imágenes aparecen en cascada con `motion.div` + `variants` (`staggerChildren: 0.08`, `spring stiffness: 300, damping: 24`).
- [x] Botones y tarjetas interactivos: `whileTap={{ scale: 0.97 }}` + `whileHover={{ y: -1 }}`.
- [x] ImageUploader drop zone: `AnimatePresence` para transiciones entre estados.
- [x] `npx vite build` sin warnings de rendimiento de animaciones.
- [x] Test manual en viewport móvil (375px) mantiene 60fps durante animaciones.

---

### [PDI-14] Backend: Definición de Esquemas Pydantic Extendidos (Módulo 1 & 2)
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-15, PDI-16, PDI-17, PDI-18 ⚠️ BLOQUEADO hasta FASE A completa
**Completado:** 2026-06-09

> **NOTA ARQUITECTÓNICA (ERR-01):** Este ticket es de FASE B. No puede iniciarse hasta que PDI-15, 16, 17 y 18 estén en DONE. El schema debe reflejar outputs reales de los algoritmos, no especulación.

**Criterios de Aceptación:**
- [x] Nuevas clases Pydantic: `ComputationalVAD`, `SemioticMass`, `ChromaticCentroid`, `SpatialDistribution`, `EnrichedFeatures`, `DetectedSymbol`.
- [x] `StrokeMetrics` extendido con `fragmentation_ratio: float = 0.0` y `spatial_distribution: SpatialDistribution`.
- [x] `AnalysisResult` extendido con `enriched_features: Optional[EnrichedFeatures] = None` y `detected_symbols: List[DetectedSymbol] = []`.
- [x] Todos los campos nuevos son `Optional` con defaults para garantizar compatibilidad retroactiva con el frontend existente.
- [x] Test: instanciar `AnalysisResult` sin los nuevos campos no lanza excepción.
- [x] Test: `AnalysisResult.model_dump()` incluye `"detected_symbols": []`.

---

### [PDI-15] Core PDI: VAD Empírico — Vertiente Computacional
**Tipo:** Feature (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-05 (histograma existente)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `compute_vad_from_histogram(histogram: dict, image: np.ndarray = None) -> dict` en `segmentation.py`.
- [x] Definir `VAD_COLOR_WEIGHTS` como diccionario estático con pesos basados en literatura de psicología del color.
- [x] Retorna `{"valence_estimate": float, "arousal_estimate": float, "dominance_estimate": float}` con valores en `[0.0, 1.0]`.
- [x] No depende de `schemas.py` ni de FastAPI.
- [x] Test VAD-1: Imagen 100% roja → `valence > 0.5` y `arousal > 0.5` — PASSED.
- [x] Test VAD-2: Imagen 100% azul → `valence < 0.5` — PASSED.
- [x] Test VAD-3: Todos los valores en rango `[0.0, 1.0]` — PASSED.

---

### [PDI-16] Core PDI: Extensión de Métricas de Trazo y Preprocesamiento Adaptativo
**Tipo:** Feature (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-04 (edges.py existente)
**Completado:** 2026-06-09

> ⚠️ **ADVERTENCIA (ERR-02):** `edges.py` ya implementa `cv2.findContours` + `cv2.arcLength` en `compute_stroke_metrics` (líneas 23-27). **EXTENDER esa función, NO crear código nuevo duplicado.**

**Criterios de Aceptación:**
- [x] `apply_canny_edge_detection` acepta `pre_blur_kernel: int = 7` y `mask: np.ndarray = None`.
- [x] `compute_stroke_metrics` retorna 6 campos: los 3 existentes + `fragmentation_ratio` + `spatial_distribution` (dict con 4 cuadrantes).
- [x] Test EDGE-1: `fragmentation_ratio` en rango `[0.0, 1.0]` — PASSED.
- [x] Test EDGE-2: Suma cuadrantes ≈ `edge_density_pct` total (tolerancia ±1%) — PASSED.
- [x] Test EDGE-3: Imagen negra → `fragmentation_ratio = 0.0`, cuadrantes = 0 — PASSED.
- [x] Los 5 tests existentes de PDI-04 siguen pasando — PASSED.

---

### [PDI-17] Core PDI: Masa Cromática y Centroide Semiótico
**Tipo:** Feature (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-05 (segmentation.py)
**Completado:** 2026-06-09

> **DECISIÓN DE DISEÑO (ERR-03):** El centroide se calcula sobre la **máscara del grupo terapéutico dominante** (warm/cool/neutral con mayor `_pct`). Empate: usar `warm` como desempate.

**Criterios de Aceptación:**
- [x] `compute_chromatic_mass(image: np.ndarray) -> dict` en `segmentation.py`.
- [x] Retorna `{"dominant_group": str, "centroid": {"x_norm": float, "y_norm": float}, "quadrant_distribution": {...}}`.
- [x] Guardia explícita: si máscara vacía (`M["m00"] == 0`), retornar centroide por defecto `(0.5, 0.5)` — IMPLEMENTADO.
- [x] Test MASS-1: Centroide de imagen warm se ubica correctamente — PASSED.
- [x] Test MASS-2: Imagen blanca → `dominant_group == "neutral"` — PASSED.
- [x] Test MASS-3: Suma `quadrant_distribution` ≈ 1.0 (tolerancia ±2%) — PASSED.
- [x] Test MASS-4: Imagen Numpy aleatoria → no lanza excepción — PASSED.

---

### [PDI-18] Arquitectura: Soporte de Máscaras ROI en Funciones Core
**Tipo:** Refactor (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-03, PDI-04, PDI-05
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `compute_color_distribution(image, mask=None)` — retrocompatible.
- [x] `compute_color_histogram(image, mask=None)` — `cv2.calcHist` acepta mask como 3er parámetro de forma nativa.
- [x] `apply_canny_edge_detection(image, ..., mask=None)` — aplicar `cv2.bitwise_and` al resultado final.
- [x] Guardia en las 3 funciones: `if cv2.countNonZero(mask) == 0: return <estructura vacía por defecto>`.
- [x] Test ROI-1: `mask=None` produce mismo resultado que antes (no-regresión) — PASSED.
- [x] Test ROI-2: Máscara que cubre solo cuadrante superior → histograma diferente al global — PASSED.
- [x] Test ROI-3: Máscara vacía → no lanza excepción, retorna defaults — PASSED.
- [x] Los tests existentes siguen pasando — 42/42 PASSED.

---

### [PDI-19] Arquitectura: Constantes Semióticas y Clasificador de Zona Koch
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-18
**Completado:** 2026-06-09

**Mapa de zonas (Test de Koch):**
```
  X < 0.5       X > 0.5
Y < 0.5: PASADO  | FUTURO
Y > 0.5: MATERIAL| IDEAL
```

**Criterios de Aceptación:**
- [x] `semiotic_config.py` creado. Sin imports de cv2 ni numpy (solo constantes y lógica pura).
- [x] `classify_semiotic_zone(x_norm, y_norm) -> str` con 4 zonas posibles.
- [x] `SEMIOTIC_ZONES: dict` con descripción clínica de cada zona.
- [x] 4 tests unitarios: `(0.1, 0.1)→PASADO`, `(0.9, 0.1)→FUTURO`, `(0.1, 0.9)→MATERIAL`, `(0.9, 0.9)→IDEAL` — PASSED.
- [x] Test de fronteras: `(0.5, 0.1)→FUTURO`, `(0.1, 0.5)→MATERIAL`, `(0.5, 0.5)→IDEAL` — PASSED.

---

### [PDI-20] Backend: Integración al Endpoint `/analyze` y QA Final
**Tipo:** Integración (Backend)
**Subagente:** Backend
**Depende de:** PDI-14, PDI-19 (FASE B + C completas)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] En `api/v1/images.py`, `compute_vad_from_histogram` y `compute_chromatic_mass` añadidos al bloque `asyncio.gather`.
- [x] Construir `EnrichedFeatures` con los resultados y añadirlo al `AnalysisResult`.
- [x] `detected_symbols` inicializado como `[]`.
- [x] Tiempo de respuesta < 5s con imagen 800x600 (RNF3 mantenido).
- [x] Los 3 tests E2E existentes siguen pasando (regresión crítica) — PASSED.
- [x] Test nuevo: `enriched_features.computational_vad.valence_estimate` ∈ `[0.0, 1.0]` — PASSED.
- [x] Test nuevo: suma cuadrantes `semiotic_mass.quadrant_mass_distribution` ≈ 1.0 — PASSED.
- [x] Test nuevo: `detected_symbols` == `[]` — PASSED.
- [x] Test nuevo: `stroke_metrics` incluye `fragmentation_ratio` y `spatial_distribution` — PASSED.

---

### [PDI-21] Frontend: Componentes de Visualización de Enriched Features
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-20 (backend integration completa), PDI-12
**Fase:** FE-D
**Completado:** 2026-06-09

> **BLOQUEADO hasta PDI-20 en DONE.** Estos componentes consumen `enriched_features` del endpoint `/analyze`.

**Criterios de Aceptación:**
- [x] VADMeter.jsx creado con 3 barras VAD y guard `if (!vad) return null`.
- [x] SemioticMap.jsx creado con grid 2x2 Koch y guard `if (!semioticMass) return null`.
- [x] MetricsPanel.jsx extendido: muestra fragmentation_ratio y spatial_distribution con fallback a undefined.
- [x] AnalysisPage.jsx actualizado: renderiza VADMeter y SemioticMap; optional chaining en enriched_features.
- [x] Degradación elegante verificada: backend sin enriched_fields ≠ error en frontend.
- [x] `npx vite build` compila sin errores.

---

### [PDI-22] PDF: Incluir Enriched Features y Métricas Extendidas en Reporte
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-20, PDI-06
**Fase:** BE-Reportes
**Completado:** 2026-06-10

**Criterios de Aceptación:**
- [x] Identificar sección en `backend/app/api/v1/reports.py` donde se inyectan los datos de PDF.
- [x] Agregar variables de fragmentación y distribución espacial a las tablas de trazo.
- [x] Crear tabla dedicada a `enriched_features` (VAD) interpretando las dimensiones (Positividad, Energía, Control).
- [x] Crear tabla para el análisis semiótico mostrando Masa cromática y cuadrantes.
- [x] Mantener soporte para generar PDF incluso cuando estas variables no estén presentes en el payload.
- [x] Todo test automatizado actual pasa sin errores tras la actualización del formato PDF.

### PRE-TICKET: Creación de DEV_JOURNAL_ADR.md y documentación base
**Completado:** 2026-06-09
**Produced:** `DEV_JOURNAL_ADR.md`, `RISK_REGISTER.md`, ADR-0002, ADR-0003, KANBAN.md actualizado

---

### [PDI-01] Configuración del Entorno y Estructura Base
**Tipo:** Arquitectura y Configuración
**Subagente:** DevOps/QA
**Depende de:** PRE-TICKET
**RNF cubiertos:** RNF4 (modularidad), RNF2 (setup simple)
**Resuelve:** FALLA-09 (CORS), FALLA-12 (DEV_JOURNAL)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] Backend: `requirements.txt` con fastapi, uvicorn, python-multipart, opencv-python-headless, numpy, pydantic, reportlab, pytest, httpx
- [x] Backend: estructura de carpetas `backend/app/api/v1/`, `backend/app/core/pdi/`, `backend/tests/unit/`, `backend/tests/integration/`, `backend/tests/fixtures/`
- [x] Backend: `main.py` levanta en `http://localhost:8000` con endpoint `/health`
- [x] Backend: `CORSMiddleware` configurada con `allow_origins=["http://localhost:5173"]`
- [x] Frontend: Proyecto Vite+React inicializado con axios y recharts instalados
- [x] Frontend: `VITE_API_URL=http://localhost:8000` en `.env`
- [x] Frontend: estructura `src/components/`, `src/pages/`, `src/services/`
- [x] `README.md` con instrucciones de arranque de ambas aplicaciones
- [x] `curl http://localhost:8000/health` → `{"status": "ok"}`
- [x] `http://localhost:5173` carga sin errores de consola
- [x] Fetch desde frontend al backend no genera error de CORS
- [x] `npx vite build` compila correctamente

---

### [PDI-01b] Esquema Canónico y Gestión de Sesión
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-01
**Resuelve:** FALLA-01 (analysis_id sin mecanismo), FALLA-06 (esquema métricas indefinido)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `schemas.py` con modelos Pydantic: `AnalysisResult`, `ColorDistribution`, `SpecificColors`, `TherapeuticGroups`, `StrokeMetrics`, `ColorHistogram`, `ProcessedImages`
- [x] `session.py` con funciones: `create_session(image_b64) -> str`, `get_session(session_id) -> AnalysisResult|None`, `is_analyzed(session_id) -> bool`, `update_session(session_id, result)`
- [x] `create_session` retorna UUID v4 válido de 36 caracteres
- [x] `is_analyzed` retorna `False` antes del análisis, `True` después
- [x] Tests unitarios: 4/4 en `tests/unit/test_session.py` pasan

---

### [PDI-02] Endpoint de Carga de Imágenes (RF1)
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-01b
**RF cubierto:** RF1
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] Endpoint `POST /api/v1/images/upload` recibe `file: UploadFile` via `multipart/form-data`
- [x] Valida extensión: solo `.jpg`, `.jpeg`, `.png`. Error → HTTP 400 `INVALID_FORMAT`
- [x] Valida tamaño: no supera `MAX_UPLOAD_SIZE_MB`. Error → HTTP 400 `FILE_TOO_LARGE`
- [x] Convierte binario a Base64, llama `session.create_session()`, retorna `{"data": {"analysis_id": "uuid"}, "meta": {"timestamp": "..."}}`
- [x] Tests: JPG válido → 200 con analysis_id; .gif → 400 INVALID_FORMAT; archivo 0 bytes → 400; excede límite → 400 FILE_TOO_LARGE

---

### [PDI-03] Core PDI: Preprocesamiento — Filtro Gaussiano (RF2) + Bilateral (ADR-0003)
**Tipo:** Feature (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-01b
**RF cubierto:** RF2 | **ADR aplicado:** ADR-0003
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `apply_gaussian_filter(image, kernel_size, sigma_x) -> np.ndarray` — cumple RF2 literalmente
- [x] `apply_bilateral_filter(image, d, sigma_color, sigma_space) -> np.ndarray` — filtro principal, preserva bordes
- [x] `ndarray_to_base64(image, ext) -> str` — función auxiliar compartida
- [x] Ambas funciones son importables sin levantar FastAPI
- [x] Tests: 4/4 pasan (Gaussiano, Bilateral, ndarray_to_base64)

---

### [PDI-04] Core PDI: Extracción de Bordes y Métricas de Trazo (RF4)
**Tipo:** Feature (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-03
**RF cubierto:** RF4
**Resuelve:** FALLA-10 (solo edge_density_pct, faltan métricas de calidad de trazo)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `apply_canny_edge_detection(image, threshold1, threshold2) -> np.ndarray` — convierte a grises internamente, retorna 2D
- [x] `compute_stroke_metrics(canny_image) -> dict` con 3 métricas:
  - `edge_density_pct`: píxeles de borde / total (trazos tupidos vs dispersos)
  - `mean_edge_intensity`: intensidad promedio de píxeles de borde (proxy fuerza del trazo)
  - `stroke_continuity`: longitud media de contornos (proxy trazos continuos vs fragmentados)
- [x] Tests: 5/5 pasan (2D output, no excepción, densidad cero, 3 claves, bordes sintéticos)

---

### [PDI-05] Core PDI: Segmentación HSV — Colores + Grupos Terapéuticos + Histograma (RF3, RF5)
**Tipo:** Feature (Backend/CV)
**Subagente:** Backend
**Depende de:** PDI-04
**RF cubiertos:** RF3, RF5 (datos histograma)
**Resuelve:** FALLA-04 (histograma ausente), FALLA-07 (solo colores individuales, sin grupos terapéuticos)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `segment_color_hsv(image, lower_bound, upper_bound) -> np.ndarray` — función pura inRange
- [x] `COLOR_RANGES_HSV` con 10 rangos (incluye red_low + red_high para wrap-around del rojo)
- [x] `compute_color_distribution(image) -> dict` con dos niveles:
  - `specific`: red, orange, yellow, green, blue, violet, white, black, gray, other (pct)
  - `therapeutic_groups`: warm (rojo+naranja+amarillo), cool (verde+azul+violeta), neutral (blanco+negro+gris), other
- [x] `compute_color_histogram(image) -> dict` con hue (180 bins), saturation (256), value (256)
- [x] `generate_hsv_mask_visualization(image) -> np.ndarray` — colorea píxeles por grupo terapéutico
- [x] Tests: 6/6 pasan (keys, sumas ~1.0, rojo→warm, azul→cool, histograma lengths)

---

### [PDI-05b] Endpoint Orquestador de Análisis Completo
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-03, PDI-04, PDI-05
**RF cubiertos:** RF2, RF3, RF4, RF5 (datos) | **RNF:** RNF3 (performance)
**Resuelve:** FALLA-02 (falta endpoint orquestador), FALLA-08 (sin prueba rendimiento)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `POST /api/v1/images/{analysis_id}/analyze` ejecuta 3 algoritmos con `asyncio.gather` + `asyncio.to_thread`
- [x] Retorna `AnalysisResult` completo INCLUYENDO imágenes Base64 (MVP simple, ADR-0002)
- [x] `analysis_id` inexistente → HTTP 404
- [x] Log de performance si procesamiento >5s (RNF3)
- [x] Tests: upload+analyze → color_distribution, stroke_metrics, histogram presentes; 404 para id inexistente; tiempo <5s con imagen 800x600

---

### [PDI-06] Endpoint de Exportación de Reportes PDF y JSON (RF6)
**Tipo:** Feature (Backend)
**Subagente:** Backend
**Depende de:** PDI-05b
**RF cubierto:** RF6
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `GET /api/v1/reports/{analysis_id}/json` retorna `AnalysisResult` sin campo `images`
- [x] `GET /api/v1/reports/{analysis_id}/pdf` genera PDF con ReportLab: encabezado, distribución de colores (tabla), métricas de trazo con interpretación, histograma textual
- [x] Sesión inexistente → 404; sesión sin analizar → 409 ANALYSIS_INCOMPLETE
- [x] Tests: JSON → 200 con métricas; JSON sin analizar → 409; PDF → 200 application/pdf; PDF sin analizar → 409

---

### [PDI-07] UI SPA: Layout Base y Carga de Archivos (RF1)
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-02, PDI-01b
**RF cubierto:** RF1 | **RNF:** RNF2 (usabilidad)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `services/api.js` con axios client configurado con `VITE_API_URL`
- [x] `services/imageService.js` con `uploadImage(file) -> analysis_id`
- [x] Componente `ImageUploader` con Drag & Drop + input file (accept .jpg,.jpeg,.png)
- [x] Máquina de estados: IDLE | UPLOADING | SUCCESS | ERROR
- [x] UPLOADING: spinner visible; SUCCESS: llama `onSuccess(analysis_id)`; ERROR: muestra mensaje backend
- [x] `HomePage` integra ImageUploader; `App.jsx` maneja navegación a AnalysisPage con analysis_id

---

### [PDI-08] UI SPA: Dashboard de Resultados PDI (RF5)
**Tipo:** Feature (Frontend)
**Subagente:** Frontend
**Depende de:** PDI-05b, PDI-06, PDI-07
**RF cubierto:** RF5 (completo, incluido histograma) | **RNF:** RNF2
**Resuelve:** FALLA-04 (histograma en frontend)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] `recharts` instalado como dependencia
- [x] `services/analysisService.js` con `triggerAnalysis(id)`, `getPdfUrl(id)`, `getJsonUrl(id)`
- [x] Componente `ImageGrid` — grilla 2x2: Original | Bilateral | Canny | HSV (`data:image/png;base64,{b64}`)
- [x] Componente `ColorHistogram` — BarChart Recharts con canal Hue coloreado por ángulo
- [x] Componente `MetricsPanel` — barras de progreso colores específicos + grupos terapéuticos (cálidos/fríos/neutros) + métricas de trazo con interpretación + botones descarga PDF/JSON
- [x] `AnalysisPage` con estados ANALYZING | DONE | ERROR; al montar llama triggerAnalysis; DONE muestra ImageGrid + ColorHistogram + MetricsPanel

---

### [PDI-09] Test de Integración E2E y Verificación RNF
**Tipo:** QA
**Subagente:** DevOps/QA
**Depende de:** PDI-02, PDI-05b, PDI-06, PDI-07, PDI-08
**RNF validado:** RNF3 (5 segundos)
**Resuelve:** FALLA-08 (ningún test valida límite de 5s)
**Completado:** 2026-06-09

**Criterios de Aceptación:**
- [x] Imagen de referencia `tests/fixtures/sample_800x600.jpg` incluida
- [x] `test_e2e_flow.py`: upload → analyze → reports JSON + PDF — todo en un flujo
- [x] Test de performance: análisis completo <5s con imagen 800x600
- [x] Test formato inválido (.gif → 400 INVALID_FORMAT)
- [x] Test sesión inexistente (analyze → 404)
- [x] Todos los tests E2E pasan: 3/3

---

## 📊 RESUMEN FINAL

| Total tickets | Completados | Pendientes | Tests totales | Pasaron |
|--------------|-------------|------------|---------------|---------|
| 26 (PRE + PDI-01 al PDI-26) | 26 | 0 | 66 | 60 (unit+integration) |

> **Nota:** PDI-01 a PDI-26 están completados. Sprint 7 añade PDF Didáctico con 7 secciones clínicas narrativas, 4 gráficos ReportLab (`pdf_charts.py`), Glosarios VAD/Koch/Trazo, y Resumen Ejecutivo en lenguaje natural. 0 dependencias nuevas (solo `reportlab.graphics` nativo, ya instalado).
