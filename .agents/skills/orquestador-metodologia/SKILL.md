---
name: orquestador-metodologia
description: IT Project Manager & Chief Architect
---
# SKILL 01 — Metodología Unificada del Orquestador
# IT Project Manager & Chief Architect

Esta skill define el proceso integral que rige el ciclo de vida de los proyectos. Combina principios de RUP (Fases) con tácticas Ágiles (Sprints/Shape Up) para asegurar un gobierno estructurado y adaptable.

---

## FASE 1 — DISCOVERY / INCEPTION (Alineación y Viabilidad)

**Objetivo:** Entender el problema de negocio, validar la viabilidad y alinear visión antes de escribir código.

1. **Extracción de Requerimientos:**
   - Funcionales (Qué debe hacer), No Funcionales (Atributos de calidad).
   - Usuarios, Plataforma objetivo, Integraciones, Restricciones Técnicas.
2. **Evaluación de Sistemas Existentes (Si aplica):**
   - Invocar al Analista Legacy para generar `LEGACY_HANDOFF.md`.
   - Decidir: ¿Extender la arquitectura actual o migrar?
3. **Identificación Inicial de Riesgos:**
   - Consultar la Skill de *Gestión de Riesgos*. Listar los 5-10 riesgos más obvios.
4. **Definición de Metodología de Trabajo:**
   - *Scrum híbrido:* Para proyectos con requerimientos que cambian pero necesitan entregas predecibles.
   - *Shape Up:* Para equipos autónomos y desarrollo creativo. Se definen "pitches" con tiempo limitado.
   - *Kanban:* Para flujo continuo (mantenimiento o corrección de bugs continuos).
5. **Generar PROJECT_CONTEXT.md:**
   - Documento que servirá como inyección de contexto para los agentes AI al inicio de cada sesión.

---

## FASE 2 — DESIGN / ELABORATION (Arquitectura y Blueprint)

**Objetivo:** Resolver la incertidumbre técnica y definir el "cómo" se construirá el sistema.

1. **Selección de Stack y Arquitectura:**
   - Consultar el *Catálogo de Arquitecturas*.
   - Usar el marco ATAM simplificado para evaluar tradeoffs (escalabilidad vs modificabilidad vs costo).
   - Crear **ADRs (Architecture Decision Records)** para fundamentar decisiones (usando el *Protocolo ADR*).
2. **Definición de Contratos:**
   - Modelos de datos (Schemas, ER).
   - Contratos de API (Interfaces, OpenAPI).
3. **Diseño del Equipo Multi-Agente:**
   - Analizar qué perfiles se necesitan (Backend, UI, Datos, QA, ML).
   - Usar la tool `define_subagent` para crear estos roles con instrucciones hiper-focalizadas.
4. **Bootstrapping del DEV_JOURNAL_ADR.md:**
   - Inicializar la bitácora con el Resumen Ejecutivo, el Stack, la Arquitectura y los ADRs iniciales.

---

## FASE 3 — BUILD / CONSTRUCTION (Implementación Iterativa)

**Objetivo:** Ejecutar el desarrollo mediante iteraciones controladas y minimizar riesgos de fallo del agente.

1. **Protocolo de Sprints (Delegación Segura):**
   - **Elaborar SPRINT_BRIEF:** Documento explícito con objetivo, stack exacto, restricciones, y Definition of Done (DoD) binario.
   - **Invocar Subagente:** Enviar el brief al agente especializado.
   - **Revisar SPRINT_REPORT:** Analizar el output (DONE / PARCIAL / BLOQUEADO).
2. **Verificación y Escalación:**
   - Un subagente (ej. QA) debe verificar el trabajo del subagente implementador mediante tests.
   - Si un subagente se bloquea, detiene su ejecución y escala al Orquestador. El Orquestador ajusta el diseño o genera un ADR.
3. **Mantenimiento del Contexto:**
   - Actualizar constantemente el `DEV_JOURNAL_ADR.md` tras cada sprint.
   - Revisar el *Risk Register* y actualizar estrategias de mitigación.
   - Aplicar el checklist de *Prevención de Fallos* para evitar pérdida de contexto o asunciones incorrectas.

---

## FASE 4 — LAUNCH / TRANSITION (Cierre)

**Objetivo:** Entregar el sistema verificando que se cumplan los criterios de éxito originales.

1. **QA Final y Hardening:**
   - Ejecución de pruebas end-to-end integradas. Verificación de requerimientos no funcionales.
2. **Cierre de Bitácora:**
   - Registrar las funcionalidades entregadas en el `DEV_JOURNAL_ADR.md`.
   - Listar la deuda técnica consciente restante para futuras iteraciones.
3. **Retrospectiva del Sistema (Auto-Mejora):**
   - Ejecutar la Skill de *Auto-Mejora*.
   - Evaluar métricas de éxito (Sprint Success Rate, Rework, Tool Misuse).
   - Modificar las skills del Orquestador si se detectaron cuellos de botella procesales.
