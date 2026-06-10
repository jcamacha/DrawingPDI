# SKILL: GESTIÓN DE MEMORIA Y ESTILO DE CÓDIGO

## PROPÓSITO
Estandarizar el proyecto al nivel corporativo (Google Style Guide / C++ Core Guidelines adaptados a Kotlin) para prever fugas de memoria y optimizar el rendimiento.

## PROTOCOLO
1. **Reutilización y Limpieza de Estado (Evitar GC Churn):** 
   Crear y destruir objetos constantemente satura el Recolector de Basura (Garbage Collector). Cuando el usuario requiera "reiniciar" una sesión de estudio, PROHIBIDO eliminar el ViewModel o el bloque de estado pesado. Debes implementar un método `reset()` explícito que devuelva todos los `StateFlow` a sus valores por defecto.
2. **Convenciones de Nombrado Uniformes:**
   - Variables y métodos: `camelCase`
   - Clases y Archivos: `PascalCase`
   - Constantes Clave: `UPPER_SNAKE_CASE`
3. **Formato Consistente:** No inventar márgenes extraños ni agrupaciones no estándar. Utiliza un estilo predecible alineado al formatter nativo.
