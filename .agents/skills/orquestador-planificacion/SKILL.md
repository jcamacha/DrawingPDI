# SKILL: PLANIFICACIÓN DE ÉPICAS Y TICKETS

## PROPÓSITO
Evitar que el Orquestador comience a delegar escritura de código de inmediato cuando el usuario solicita una nueva funcionalidad o refactorización masiva. Esta skill forza la etapa de descubrimiento y gestión de proyectos.

## PROTOCOLO
1. **Pausa Obligatoria:** Si el usuario pide "implementa X característica", NO generes código ni subagentes de desarrollo.
2. **Invocación del PM:** Invoca al `subagente-arquitecto-pm` pasándole los requerimientos.
3. **Validación del Kanban:** Espera a que el `subagente-arquitecto-pm` devuelva un plan de arquitectura y registre los nuevos tickets (con sus Criterios de Aceptación) en el `KANBAN.md`.
4. **Aprobación del Usuario:** Muestra el plan al usuario. Sólo cuando el usuario apruebe el ticket y los tests a realizar, se podrá proceder a delegar a un subagente de desarrollo (`frontend`, `backend`, etc.).
5. **Testing First:** Exige al desarrollador que cumpla con los requisitos de pruebas definidos por el PM (Martin Fowler Testing principles).
