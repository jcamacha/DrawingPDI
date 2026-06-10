# SKILL: ARQUITECTURA Y CÓDIGO LIMPIO

## PROPÓSITO
Asegurar una base de código robusta, evitando el secuestro de hilos y garantizando la Separación de Responsabilidades (Separation of Concerns) basados en Patrones de Diseño (Refactoring.guru / Game Programming Patterns).

## PROTOCOLO
1. **Single Point of Entry:** El archivo raíz (`MainActivity.kt`) debe permanecer impecable. Únicamente debe inyectar dependencias y levantar el grafo de navegación. Ninguna lógica de negocio gráfica pesada debe residir ahí.
2. **Asincronía y Loop Principal:** En el modelo de Jetpack Compose, el estado reactivo dicta el bucle de UI. Queda estrictamente PROHIBIDO el uso de `Thread.sleep()` o bucles `while (true)` bloqueantes en el hilo principal. Toda tarea diferida debe vivir en `viewModelScope.launch { ... }`.
3. **Patrón State (State Machine):** Para manejar estados complejos (ej. progreso de un ejercicio), utiliza clases selladas (`sealed classes`) y flujos unidireccionales. No uses anidamiento infinito de condicionales (If-Else spaghetti).
