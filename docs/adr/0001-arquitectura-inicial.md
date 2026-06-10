# 1. Arquitectura Inicial - Procesamiento Digital de Imágenes para Arteterapia

Fecha: 2026-06-09
Estado: Aceptado

## Contexto
Se requiere desarrollar un sistema informático que asista en Arteterapia utilizando técnicas de Procesamiento Digital de Imágenes (PDI). Las principales necesidades de negocio incluyen: carga de imágenes, procesamiento algorítmico (Filtro Bilateral, Canny, Segmentación HSV por colores), visualización del resultado al usuario final, y exportación de reportes detallados en formatos PDF y JSON. Todo en una arquitectura orientada a alta mantenibilidad, baja latencia y separación de responsabilidades.

## Decisiones Arquitectónicas

1. **Arquitectura Global - Cliente-Servidor Desacoplado**:
   Se adopta una arquitectura de microservicios lógicos (Frontend y Backend totalmente desacoplados).
   - **Frontend**: Single Page Application (SPA).
   - **Backend**: API RESTful stateless.

2. **Stack Tecnológico**:
   - **Backend**: FastAPI (Python). Soporte nativo para operaciones asíncronas y tipado fuerte (Pydantic), ideal para procesar I/O de red y delegar el procesamiento intensivo a hilos secundarios.
   - **Procesamiento de Imágenes (PDI)**: OpenCV (`cv2`) y NumPy.
   - **Frontend**: React.js empaquetado con Vite. Esto garantiza *Hot Module Replacement (HMR)* ultra-rápido y builds ligeros.
   - **Generación de Reportes**: `ReportLab` o `FPDF` para la exportación de documentos PDF; librerías estándar de Python para JSON.

3. **Separation of Concerns (SoC) y Estructura de Proyecto**:
   - En el Backend, los controladores (Endpoints de FastAPI) **no** deben contener lógica de negocio ni de procesamiento (Canny, Filtros, etc).
   - Se aplicará una Arquitectura en Capas estricta:
     - Capa `api/`: Define los endpoints HTTP.
     - Capa `core/pdi/`: Contiene **funciones puras** de procesamiento numérico sin conocimiento de FastAPI. Esto permite tests unitarios aislados sin necesidad de levantar el servidor web.
   - En el Frontend, los componentes de UI (Vistas) se separan de la lógica de red (custom hooks o capa de servicios).

4. **Prevención de Bloqueo del Hilo Principal (Non-blocking Main Thread)**:
   - Dado que FastAPI ejecuta un *Event Loop* asíncrono en un solo hilo, la ejecución directa de funciones de OpenCV (que son intensivas en CPU) podría congelar la API para otros usuarios.
   - Todo procesamiento de PDI (Bilateral, Canny, HSV) se debe delegar a un `ThreadPoolExecutor` utilizando `asyncio.to_thread()` de manera obligatoria.

5. **Optimización de Ejecución (Out of the Box)**:
   - **Backend**: Contará con un `requirements.txt` limpio. Para iniciar el entorno sólo requerirá: `pip install -r requirements.txt` y `uvicorn app.main:app --reload`.
   - **Frontend**: Estará configurado para arrancar limpiamente con `npm install` y `npm run dev`. No debe requerir instalaciones de bibliotecas a nivel global del OS que puedan fallar entre diferentes entornos.

## Consecuencias

* **Positivas**:
  * **Alta testeabilidad**: Las funciones puras de OpenCV se pueden testear con `pytest` introduciendo matrices numpy artificiales (mocks/fixtures) con resultados instantáneos.
  * **Escalabilidad futura**: Si el procesamiento se vuelve excesivamente pesado con usuarios recurrentes, la lógica puramente aislada facilita extraer el proceso a un Worker en background (ej. Celery + RabbitMQ/Redis).
  * **Mantenibilidad**: La separación entre React y FastAPI permite que equipos distintos trabajen en el UI y el algoritmo al mismo tiempo basándose en un contrato de API.
* **Negativas / Consideraciones**:
  * Necesitamos manejar eficientemente la transferencia de la imagen a través de la red HTTP.
  * **Decisión de Transferencia**: Se utilizará `multipart/form-data` explícitamente en el endpoint de subida para enviar la imagen en binario crudo, evitando el overhead del ~33% de tamaño que generaría una serialización en Base64.
