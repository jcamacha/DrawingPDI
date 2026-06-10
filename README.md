# PDI Arteterapia

Sistema de Procesamiento Digital de Imágenes aplicado a Arteterapia. Extrae métricas cuantitativas de pinturas (distribución de color, métricas de trazo, histograma HSV) para apoyar la evaluación clínica en sesiones de arteterapia.

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

```
backend/
├── app/
│   ├── main.py              # FastAPI app con CORS y routers
│   ├── api/v1/
│   │   ├── images.py        # Upload + Analyze endpoints
│   │   └── reports.py       # JSON + PDF report endpoints
│   └── core/pdi/
│       ├── schemas.py       # Modelos Pydantic (AnalysisResult)
│       ├── session.py       # Gestión de sesión en memoria
│       ├── filters.py       # Gaussiano + Bilateral + ndarray_to_base64
│       ├── edges.py         # Canny + métricas de trazo
│       └── segmentation.py  # HSV + grupos terapéuticos + histograma
├── tests/
│   ├── unit/                # Tests unitarios por módulo
│   └── integration/         # Tests de integración E2E de API
├── requirements.txt
└── .env.example

frontend/
├── src/
│   ├── components/          # ImageUploader, ImageGrid, ColorHistogram, MetricsPanel
│   ├── pages/               # HomePage, AnalysisPage
│   └── services/            # api.js, imageService.js, analysisService.js
├── package.json
└── .env
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/images/upload` | Subir imagen (multipart/form-data) |
| POST | `/api/v1/images/{analysis_id}/analyze` | Ejecutar análisis PDI completo |
| GET | `/api/v1/reports/{analysis_id}/json` | Reporte JSON (sin imágenes) |
| GET | `/api/v1/reports/{analysis_id}/pdf` | Reporte PDF |
