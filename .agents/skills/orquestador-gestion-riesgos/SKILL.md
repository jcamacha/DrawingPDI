---
name: orquestador-gestion-riesgos
description: Protocolo de Identificación y Mitigación
---
# SKILL 02 — Gestión de Riesgos en Proyectos de Software
# Protocolo de Identificación y Mitigación

El Orquestador debe mantener una gestión activa y documentada de riesgos para asegurar el éxito del proyecto. Esta skill define cómo manejar la incertidumbre.

## 1. Identificación de Riesgos (Inception y al inicio de sprints)
Analiza el proyecto usando categorías estándar:
- **Técnicos:** Stacks inmaduros, integraciones complejas, arquitectura no probada.
- **Procesos:** Deuda técnica, dependencias bloqueantes entre agentes.
- **Externos:** Fallos en APIs de terceros, cambios en servicios Cloud.
- **Agenticos:** Pérdida de contexto, alucinaciones en generación de código, *scope creep* autoinducido.

**Técnica FMEA (Failure Mode and Effects Analysis):**
Para componentes críticos, desglosa:
- Modo de falla: ¿Qué puede salir mal? (ej. API timeout)
- Efecto: ¿Qué pasa si ocurre? (ej. UI bloqueada)
- Causa raíz: ¿Por qué ocurre? (ej. falta de circuit breaker)
- Acción: (ej. implementar timeout + reintentos automáticos)

## 2. Clasificación (Probabilidad × Impacto)
Mide el riesgo en una matriz 5x5:
- **Impacto (1-5):** De "Mínimo" (bug cosmético) a "Crítico" (pérdida de datos, caída total).
- **Probabilidad (1-5):** De "Raro" a "Casi Seguro".
- **Score (Probabilidad x Impacto):**
  - **1-4:** Aceptar y monitorear.
  - **5-9:** Planificar mitigación a medio plazo.
  - **10-15:** Mitigación inmediata, asignar sprint prioritario.
  - **16-25:** Escalar, rediseñar arquitectura o detener ejecución.

## 3. Estrategias de Manejo
Al registrar un riesgo, asigna una de estas estrategias:
- **Evitar:** Cambiar el plan (ej. cambiar una librería inestable por la standard library).
- **Mitigar:** Reducir impacto/probabilidad (ej. escribir más tests unitarios, usar circuit breakers).
- **Aceptar:** Riesgo inherente con bajo score, se asume.
- **Contingencia:** Plan B (ej. Si la base de datos cloud falla, usar caché local temporal).

## 4. Mantenimiento del RISK_REGISTER.md
Debes crear y mantener un documento llamado `RISK_REGISTER.md` en el proyecto.
**Columnas requeridas:**
`ID` | `Descripción` | `Categoría` | `Prob` | `Imp` | `Score` | `Estrategia` | `Acción Mitigante` | `Estado`

**Regla de Revisión:** Repasa los riesgos activos al finalizar cada iteración mayor o fase del proyecto. Actualiza los scores basándote en la información reciente.
