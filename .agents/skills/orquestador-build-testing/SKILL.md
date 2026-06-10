# SKILL: BUILD OUT-OF-THE-BOX Y TESTING

## PROPÓSITO
Garantizar que el repositorio pueda ser clonado y ejecutado inmediatamente sin configuración oculta (Modern CMake / Gradle), e instaurar la cultura de pruebas empresariales de Martin Fowler.

## PROTOCOLO
1. **Entorno Out of the Box:** Prohibido insertar "Hardcoded Paths" (Rutas Absolutas) como `C:/Users/...` o requerir dependencias no declaradas en Gradle. Cualquier desarrollador debe poder clonar y correr `./gradlew assembleDebug` exitosamente.
2. **Testing como Ciudadano de Primera Clase (TDD):** Antes de mover cualquier ticket de "IN PROGRESS" a "DONE", se debe exigir evidencia de Pruebas Unitarias o de Integración locales para la nueva lógica.
3. **Code Review:** Se evaluarán las funciones buscando "Code Smells". Si un archivo pasa de 500 líneas y mezcla la UI con llamadas directas de Red o Base de datos, se debe refactorizar delegando a un Repositorio (Separation of Concerns).
