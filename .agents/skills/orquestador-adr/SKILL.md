---
name: orquestador-adr
description: Formato Nygard y Reglas de Inmutabilidad
---
# SKILL 04 — Protocolo de Architecture Decision Records (ADR)
# Formato Nygard y Reglas de Inmutabilidad

Los ADR son documentos críticos. Son la memoria histórica del "por qué" se tomó una decisión estructural, tecnológica o metodológica importante. Evitan que tú o futuros agentes reviertan decisiones valiosas por falta de contexto.

## 1. Cuándo crear un ADR
- Elección de lenguaje, framework principal o base de datos.
- Patrones arquitectónicos globales (ej. elegir MVVM vs MVI).
- Aceptación explícita de deuda técnica a favor del time-to-market.
- Decisiones que restringen las opciones futuras del sistema.
- Cambios sobre decisiones pasadas (superseding).

**NO crees ADRs para:** nombramiento de variables, refactors menores internos, estructura trivial de carpetas.

## 2. Reglas de Manejo
- **Ubicación:** Guardar en `docs/adr/`.
- **Nomenclatura:** Secuencial. Ej. `0001-uso-de-kotlin-jetpack.md`.
- **Inmutabilidad:** Una vez un ADR pasa al estado `Aceptado`, NUNCA se edita para cambiar su significado. Si la decisión se revierte meses después, se crea un nuevo ADR que indica que "supercede" al antiguo.

## 3. Plantilla Oficial (Formato Nygard)

```markdown
# ADR-NNNN: [Título corto, en formato imperativo o de decisión. Ej: Usar Room para persistencia local]

## Estado
[Propuesto | Aceptado | Deprecado | Superseded por ADR-XXXX]

## Contexto
[Descripción neutral y factual del escenario. ¿Cuál es el problema a resolver?
¿Cuáles son las restricciones del negocio y técnicas? ¿Qué provocó la necesidad de decidir hoy? Sin juicios subjetivos.]

## Decisión
[Declaración firme y directa de la resolución. Ej: "Usaremos Jetpack Room como ORM sobre SQLite para toda la persistencia local de la app".]

## Consecuencias
[Los resultados de esta decisión.
Aspectos POSITIVOS (pros) que ganamos.
Aspectos NEGATIVOS (contras) que perdemos o riesgos que asumimos.
DEUDA TÉCNICA u obligaciones futuras adquiridas.]

## Alternativas Consideradas
[¿Qué otras opciones se evaluaron y por qué fueron descartadas?
Ej: Se descartó Realm porque su huella binaria es mayor y el soporte en corrutinas es menos nativo.]
```

## 4. Flujo Práctico para el Agente
1. Detectas una divergencia o necesidad de decisión de alto impacto.
2. Usas la skill del *Catálogo de Arquitecturas* para evaluar.
3. Generas el archivo en `docs/adr/`.
4. Resumes el ADR en el archivo maestro `DEV_JOURNAL_ADR.md`.
5. Ajustas el `PROJECT_CONTEXT.md` si el ADR cambia las restricciones globales de los subagentes.
