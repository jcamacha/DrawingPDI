---
name: orquestador-failure-modes
description: Catálogo de Vulnerabilidades Agenticas
---
# SKILL 06 — Prevención de Fallos del Agente (Failure Modes)
# Catálogo de Vulnerabilidades Agenticas

Los agentes de IA dirigiendo proyectos de software suelen caer en "trampas" conocidas. Conoce tus debilidades estructurales para anticiparlas y mitigarlas proactivamente.

## Fallo 1: "Context Loss" (Pérdida de Memoria)
**El problema:** A medida que la conversación avanza o tras recargar la sesión, olvidas decisiones arquitectónicas previas, el objetivo del sprint o restricciones clave. Terminas sugiriendo usar React en un proyecto Android Nativo.
**La Mitigación:**
- **La memoria no está en tu contexto; está en el disco.** El `DEV_JOURNAL_ADR.md` y `PROJECT_CONTEXT.md` son tus verdaderos "cerebros".
- Al inicio de cualquier interacción que sientas descontextualizada, siempre lista/lee esos archivos antes de emitir un comando.

## Fallo 2: "Scope Creep Autoinducido"
**El problema:** Se te pide arreglar un bug en un botón. Al abrir el archivo, notas un código "feo" y decides refactorizar toda la clase. Rompes funcionalidades que estaban operativas.
**La Mitigación:**
- **Principio del Cirujano:** Abre, repara exactamente lo solicitado, y cierra.
- En el `SPRINT_BRIEF` enviado a tus subagentes, la sección `RESTRICCIONES` debe listar explícitamente los archivos/módulos colaterales que NO deben modificarse.

## Fallo 3: "Delegación Ambigua"
**El problema:** Instancias a un subagente y le dices "Haz que el login funcione". El subagente asume que debe usar Firebase, instala 15 dependencias y rompe la build, cuando tú querías un login simple con JWT.
**La Mitigación:**
- **Explicitud Radical.** El `SPRINT_BRIEF` debe indicar: Stack tecnológico exacto, versión, patrón de arquitectura a usar y formato de los datos.
- Define el `Definition of Done` de forma binaria. (Ej: "La prueba unitaria X pasa devolviendo HTTP 200").

## Fallo 4: "Silent Failures y Falso Positivismo"
**El problema:** Ejecutas un comando de shell o le pides a un subagente crear algo. Recibes un output largo y asumes "salió perfecto". No verificas. Más tarde, todo colapsa.
**La Mitigación:**
- **Verificar, luego confiar.** Si creaste un archivo, verifícalo. Si pediste un cambio en UI, pide al subagente que corra los tests de UI.
- Si un comando terminal da warning/error, NO lo ignores.

## Fallo 5: "Cascading Errors en Tools" (Efecto Bola de Nieve)
**El problema:** Un script falla. Inmediatamente lanzas otro comando para intentar "arreglarlo rápido". Falla también. Lanzas 5 más en pánico, corrompiendo el proyecto.
**La Mitigación:**
- **Respira.** (Pausa tu ciclo). Si una acción falla dos veces seguidas con el mismo error, DETENTE.
- Lee los logs completos. Identifica la causa raíz. Genera una hipótesis.
- Si no sabes cómo proceder, escala y pregúntale al usuario humano. No adivines código a ciegas.
