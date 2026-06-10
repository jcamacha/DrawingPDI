# PDI Arteterapia

Sistema Avanzado de Procesamiento Digital de Imágenes aplicado a Arteterapia. Extrae métricas cuantitativas y cualitativas de producciones artísticas para apoyar la evaluación clínica.

**Nuevas características:**
- **Métricas de Trazo y Color:** Densidad de bordes, continuidad, proporción HSV.
- **Análisis Emocional (VAD):** Dimensiones computacionales de Valencia (Positividad), Activación (Energía) y Dominancia (Control).
- **Prueba Semiótica de Koch:** Distribución de masa cromática espacial para inferir cuadrantes psicológicos (Pasado, Futuro, Material, Ideal).
- **Reportes Didácticos:** Generación de un PDF clínico con gráficas ReportLab (barras VAD, pastel terapéutico, mapa de Koch) e interpretaciones en lenguaje natural.

## Requisitos

- Python 3.11+
- Node.js 18+ (para el frontend)

## Configuración del Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Configuración del Frontend

```bash
cd frontend
npm install
npm run dev
```

## Verificar instalación

```bash
# Backend
cd backend
python3 -c "from app.main import app; print('Backend imports OK')"

# Frontend
cd frontend
npx vite build
```

## Ejecutar Tests

```bash
cd backend
python3 -m pytest tests/ -v
```

## Estructura del Proyecto

```text
backend/
├── app/
│   ├── main.py              # FastAPI app con CORS y routers
│   ├── api/v1/
│   │   ├── images.py        # Upload + Analyze endpoints
│   │   ├── reports.py       # Reporte PDF Didáctico (Narrativo) + JSON
│   │   └── pdf_charts.py    # Generación de gráficos (ReportLab en memoria)
│   └── core/pdi/
│       ├── schemas.py       # Modelos Pydantic (VAD, Semiotic, AnalysisResult)
│       ├── session.py       # Gestión de sesión en memoria
│       ├── filters.py       # Gaussiano + Bilateral + base64 utils
│       ├── edges.py         # Canny + métricas de trazo (fragmentación, densidad)
│       ├── segmentation.py  # HSV + grupos terapéuticos + masa cromática
│       └── semiotic_config.py # Clasificador Koch espacial
├── tests/
│   ├── unit/                # Tests unitarios (core, charts)
│   └── integration/         # Tests E2E de endpoints y PDFs
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── components/          # VADMeter, SemioticMap, ColorHistogram, MetricsPanel, etc.
│   ├── pages/               # HomePage, AnalysisPage
│   └── services/            # APIs
├── package.json
└── .env
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/images/upload` | Subir imagen (multipart/form-data) |
| POST | `/api/v1/images/{analysis_id}/analyze` | Ejecutar análisis PDI completo |
| GET | `/api/v1/reports/{analysis_id}/json` | Reporte JSON (incluye VAD, Semiótica, Trazo) |
| GET | `/api/v1/reports/{analysis_id}/pdf` | Reporte PDF Didáctico con Gráficos |
