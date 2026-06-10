---
name: orquestador-arquitecturas
description: Protocolo de Decisión Estructural (ATAM Simplificado)
---
# SKILL 03 — Catálogo de Arquitecturas y Evaluación
# Protocolo de Decisión Estructural (ATAM Simplificado)

Tu responsabilidad como Arquitecto Jefe es seleccionar el patrón arquitectónico óptimo evaluando de manera objetiva los "tradeoffs", nunca por moda o sesgo de entrenamiento.

## 1. Criterios de Evaluación (ATAM Simplificado)
Antes de elegir la arquitectura, pondera los siguientes atributos de calidad para el proyecto en curso:
- **Modificabilidad:** ¿Con qué frecuencia cambiarán las reglas de negocio?
- **Escalabilidad:** ¿Cuál es el tráfico esperado? ¿Hay cuellos de botella claros?
- **Testeabilidad:** ¿Es crítico hacer mock de la infraestructura para pruebas aisladas?
- **Despliegue/Operaciones:** ¿Tenemos recursos (subagentes DevOps) para mantener infraestructura compleja?
- **Time-to-Market:** ¿Es un MVP que debe lanzarse ya?

## 2. Patrones Arquitectónicos Base

| Arquitectura | Cuándo Elegirla | Tradeoffs Principales |
|---|---|---|
| **Monolito Clásico** | MVPs, proyectos personales, equipos muy pequeños (o 1 solo agente). | + Rápido de construir y desplegar. <br> - Se vuelve "spaghetti" rápido si no hay disciplina. |
| **Monolito Modular** | Sistemas empresariales de tamaño medio. El balance ideal. | + Lógica separada por dominio, despliegue simple. <br> - Requiere disciplina estricta de interfaces internas. |
| **Microservicios** | Escalabilidad masiva requerida para dominios independientes. | + Escalado individual, tolerancia a fallos aislada. <br> - Complejidad operacional masiva (DevOps, latencia red). |
| **Hexagonal (Ports & Adapters)** | Lógica de negocio compleja que debe aislarse de UI y DB. | + Testeabilidad total, agnóstico a frameworks. <br> - Curva de aprendizaje y boilerplate inicial alto. |
| **Event-Driven / CQRS** | Alta asincronía, lecturas y escrituras muy dispares, auditoría. | + Altamente desacoplado, reconstrucción de estado. <br> - Consistencia eventual, extrema complejidad de debugging. |

## 3. Patrones por Dominio Específico

| Dominio | Patrón Recomendado | Persistencia Común |
|---|---|---|
| **Móvil Android Nativo** | MVVM + Clean Architecture / Repository | Room (SQLite), DataStore |
| **Móvil iOS Nativo** | MVVM-C (Coordinators) / Clean Architecture | CoreData, SwiftData |
| **APIs REST / Backend** | Capas (Controller-Service-Repo) + Hexagonal interno | ORMs (Prisma, Hibernate, GORM) |
| **Sistemas ML / IA** | Separación: Inferencia (API) vs Entrenamiento (Pipeline DAG) | Feature Stores, Vector DBs |
| **Aplicaciones LLM (RAG)** | Indexer + Retriever + Generator (Agentic Loops) | Pinecone, Chroma, pgvector |
| **Frontend Web** | Componentes aislados, Gestión de Estado Global (Redux, Zustand) | LocalStorage, IndexedDB |

## 4. Reglas de Oro Arquitectónicas
1. **Empieza Simple:** El *Majestic Modular Monolith* es casi siempre la mejor opción inicial.
2. **Ley de Conway:** La arquitectura reflejará la organización del equipo. Define tus subagentes reflejando tus módulos.
3. **El Centro es Sagrado:** La lógica de dominio nunca debe depender de frameworks de interfaz de usuario ni de drivers de base de datos concretos (aplica principios SOLID e Inversión de Dependencias).
