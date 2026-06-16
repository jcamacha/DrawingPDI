# PDI Arteterapia: Sistema Avanzado para el Apoyo en el Diagnóstico Psicológico

## Introducción

Bienvenido a **PDI Arteterapia**, una herramienta tecnológica orientada a potenciar y apoyar la labor de psicólogos y terapeutas durante el proceso de diagnóstico y seguimiento clínico en terapia.

A través de técnicas avanzadas de Procesamiento Digital de Imágenes (PDI), este sistema analiza producciones artísticas realizadas por los pacientes, proveyendo al profesional de la salud mental de métricas cuantitativas y cualitativas de forma rápida, estructurada y automatizada.

## Objetivo del Proyecto

El objetivo principal de este sistema es ofrecer un instrumento de evaluación complementario para los terapeutas. Al extraer características visuales clave del dibujo, el sistema mapea estos elementos a diversas métricas emocionales y psicológicas. Esto facilita significativamente la interpretación clínica, ayudando a enfocar el tratamiento y a comprender de manera más profunda e integral el estado interno y emocional del paciente.

## Flujo de Trabajo del Sistema

El sistema ha sido diseñado para integrarse fluidamente en la práctica clínica, siguiendo un flujo de trabajo intuitivo y efectivo:

1. **Expresión Libre (La Prueba):** Se le solicita al paciente que realice un dibujo libre. Se recomienda y fomenta fuertemente el uso de **colores pastel**, ya que es un material sumamente didáctico y moldeable que facilita la conexión emocional y permite una mejor expresión por parte de los pacientes.
2. **Captura Fotográfica:** Una vez que el paciente finaliza el dibujo, el terapeuta toma una fotografía de la obra generada utilizando cualquier dispositivo con cámara.
3. **Carga al Sistema:** El terapeuta ingresa a la plataforma web de PDI Arteterapia y sube la imagen del dibujo.
4. **Procesamiento Digital de Imágenes (PDI):** El pipeline de procesamiento del sistema entra en acción de manera automática:
   - **Análisis de Color:** Extrae los colores que presentan un mayor porcentaje de área en el dibujo y los mapea a diferentes métricas emocionales.
   - **Análisis de Trazo:** Mediante el uso de un detector de bordes, el sistema evalúa la calidad del trazo y la intencionalidad con la que el paciente plasmó el dibujo sobre el papel.
5. **Detección de Objetos y Análisis Semiótico (Futura Implementación):** Se tiene contemplado incluir un detector de objetos asistido por un agente de Inteligencia Artificial. Este agente se encargará de visualizar el objeto dibujado e identificar su significado semiótico, interpretando los recursos simbólicos que el paciente haya empleado para expresar su idea o vivencia.
6. **Generación de Reportes para Tratamiento:** Finalmente, el sistema genera de forma automática un **PDF Clínico y Didáctico** orientado al terapeuta. Este documento incluye diversas métricas y gráficas que sirven como apoyo sustancial para planificar y ajustar el tratamiento del paciente.

---

## Características Técnicas Actuales

- **Métricas de Trazo y Color:** Densidad de bordes, continuidad, proporción HSV.
- **Análisis Emocional (VAD):** Dimensiones computacionales de Valencia (Positividad), Activación (Energía) y Dominancia (Control).
- **Prueba Semiótica de Koch:** Distribución de masa cromática espacial para inferir cuadrantes psicológicos (Pasado, Futuro, Material, Ideal).
- **AI Context Builder (Nuevo):** Pipeline avanzado que detecta regiones de color y construye un contexto estructurado con métricas locales, relaciones de proximidad e interpretaciones heurísticas empíricas. Diseñado para alimentar a un agente de IA encargado de redactar reportes.
- **Reportes Didácticos Cuantitativos:** Generación de un PDF clínico estructurado en 7 secciones narrativas y éticamente limitadas (incluyendo Resumen Ejecutivo, Perfil Emocional VAD, Fenotipado Espacial y Anexo Técnico), asegurando un enfoque descriptivo y no diagnóstico apoyado por gráficos ReportLab.

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
│       ├── semiotic_config.py # Clasificador Koch espacial
│       └── ai_context_builder.py # Constructor de contexto para el agente IA
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
