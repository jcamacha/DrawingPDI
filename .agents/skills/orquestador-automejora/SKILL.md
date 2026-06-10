---
name: orquestador-automejora
description: Proceso de Retrospectiva y Actualización
---
# SKILL 05 — Auto-Mejora y Metacognición
# Proceso de Retrospectiva y Actualización

Como agente AI avanzado, no eres infalible, pero posees la capacidad crítica de **auto-observación**. Esta skill define tu proceso de aprendizaje continuo para no repetir el mismo error en múltiples proyectos o sprints.

## 1. El Bucle de Metacognición

Tu funcionamiento no es solo "recibir prompt -> ejecutar". Debes integrar el paradigma **Reflexion**:
1. **Ejecutar** (Lanzar un subagente, modificar código, crear arquitectura).
2. **Observar** (Revisar el output, evaluar el resultado de QA o compilación).
3. **Reflexionar** (¿Salió bien? ¿Por qué falló? ¿El SPRINT_BRIEF fue ambiguo?).
4. **Almacenar y Corregir** (Ajustar el próximo prompt o documentar el error).

**Cuidado con la "Trampa de Coherencia":** Es fácil autoconvencerse de que un código erróneo está bien argumentándolo lógicamente. Por eso, **siempre** confía en los tests, logs del compilador y el feedback explícito del usuario por encima de tus propias asunciones teóricas.

## 2. Retrospectivas Automáticas
Al final de cada fase importante o Sprint complejo, el Orquestador debe generar un breve bloque de retrospectiva en el `DEV_JOURNAL_ADR.md`.

**Formato de Retrospectiva:**
- **Éxitos:** Qué funcionó rápido y sin errores.
- **Fallos del Agente:** ¿Perdí contexto? ¿Modifiqué archivos sin permiso? ¿Me enfoqué en optimizar algo que no se pidió?
- **Ajustes:** Acciones concretas para el próximo sprint (Ej: "Añadiré una restricción explícita en el SPRINT_BRIEF para que el subagente de UI no modifique el DAO de Room").

## 3. Actualización de Knowledge Base
Si detectas un problema sistemático, tienes autoridad para **modificar tus propios archivos de skills** (en `.agents/skills/`) para prevenirlo en el futuro.

**Pasos para modificar una skill:**
1. **Detectar:** El fallo ocurre más de 2 veces de la misma forma.
2. **Abstraer:** ¿Cuál es la regla general que evita esto? (Ej: "Nunca sobreescribir la configuración del linter sin preguntar al usuario").
3. **Codificar:** Usa la tool de escritura para agregar esta nueva regla a tu checklist correspondiente en `.agents/skills/`.
4. **Registrar:** Añade una entrada al DEV_JOURNAL indicando que tu base de conocimientos fue actualizada para ser más eficiente.

## 4. Métricas de Salud del Proyecto AI
Monitorea inconscientemente estas métricas para saber cuándo intervenir:
- **Sprint Success Rate:** ¿Cuántos subagentes logran `DONE` al primer intento sin rebotar errores de compilación?
- **Rework Rate:** ¿Cuántas veces tienes que pedirle al mismo subagente que arregle lo que acaba de romper?
- **Scope Adherence:** ¿Estamos resolviendo el ticket actual o nos desviamos refactorizando otra cosa?
