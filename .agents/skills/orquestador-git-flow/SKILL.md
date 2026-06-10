# SKILL: GIT FLOW Y CONVENTIONAL COMMITS

## PROPÓSITO
Replicar el nivel de profesionalismo de la industria del software (Pro Git) garantizando que la trazabilidad entre el código y la planificación (Jira/Kanban) sea perfecta.

## PROTOCOLO DE COMMITS
1. **Aislamiento:** Está estrictamente prohibido acumular múltiples tareas no relacionadas en un solo commit ("commit gigante"). Los commits deben ser atómicos.
2. **Referencia a Ticket:** Todo commit DEBE contener el ID del ticket del Kanban que está resolviendo.
3. **Convención:** Usar siempre *Conventional Commits*:
   - `feat([modulo]): [TICKET-ID] Descripción` (Para nuevas características)
   - `fix([modulo]): [TICKET-ID] Descripción` (Para solución de bugs)
   - `docs([modulo]): [TICKET-ID] Descripción` (Para actualizaciones de documentación)
   - `test([modulo]): [TICKET-ID] Descripción` (Para inclusión de pruebas unitarias o de integración)
   - `refactor([modulo]): [TICKET-ID] Descripción` (Para cambios que no añaden feature ni arreglan bug, ej. reordenamiento)

## EJEMPLO CORRECTO
`git commit -m "feat(ui): [APP-12] implementar botón de guardado en el diccionario"`

## EJEMPLO INCORRECTO
`git commit -m "update files"`
