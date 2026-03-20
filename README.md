# Copiloto Clínico de Procesamiento de Lenguaje Natural (NLP)

> Transformando historias clínicas en inteligencia médica accionable  
> **Versión 1.0 · 2026**

---

## Resumen Ejecutivo

Este documento define el proyecto técnico completo del Copiloto Clínico NLP, una herramienta de inteligencia artificial diseñada para transformar historias clínicas en texto libre en **Resúmenes Ejecutivos Técnicos** estructurados, optimizados para la toma de decisiones médicas.

El proyecto se estructura en tres fases progresivas:

- **Fase 1** — Fundamentos técnicos: infraestructura, dataset y pipeline de evaluación
- **Fase 2** — Evaluación y comparación de modelos LLM (genéricos, comunitarios y personalizado)
- **Fase 3** — Colaboración médica, validación clínica y visión de producto a futuro

---

## Tabla de Contenidos

1. [Contexto del Proyecto](#1-contexto-del-proyecto)
2. [Fase 1 — Fundamentos Técnicos](#2-fase-1--fundamentos-técnicos)
3. [Fase 2 — Evaluación de Modelos](#3-fase-2--evaluación-de-modelos)
4. [Fase 3 — Validación Clínica](#4-fase-3--validación-clínica)
5. [Versión 3 — Visión Futura](#5-versión-3--visión-futura-del-producto)
6. [Plan de Trabajo](#6-plan-de-trabajo)
7. [Preguntas Abiertas](#7-preguntas-abiertas)

---

## 1. Contexto del Proyecto

### 1.1 Problemática

Los médicos enfrentan tres barreras críticas que afectan directamente la calidad de la atención:

| Problema | Severidad | Descripción |
|---|---|---|
| **Inercia clínica por sobrecarga** | 🔴 CRÍTICA | El médico invierte la mayor parte del tiempo de consulta leyendo notas previas, retrasando la interacción directa con el paciente |
| **Dispersión de información** | 🟠 ALTA | Los hitos clave como alergias, cambios de conducta y motivos de descompensación se diluyen en párrafos extensos y repetitivos |
| **Riesgo de omisión** | 🔴 SEVERA | La presión asistencial puede llevar a pasar por alto observaciones vitales para el ajuste terapéutico, comprometiendo la seguridad del paciente |

### 1.2 Solución Propuesta

El Copiloto Clínico NLP analiza historias clínicas en texto libre y genera un **Resumen Ejecutivo Técnico** estructurado en tres componentes:

- **Trayectoria Clínica** — Evolución técnica desde el primer registro hasta la consulta actual
- **Intervenciones Consolidadas** — Cambios terapéuticos y sus resultados documentados
- **Estado de Seguridad** — Alertas críticas: alergias, contraindicaciones y reacciones adversas

### 1.3 Objetivo Tecnico General

> Determinar si modelos de lenguaje locales (open-weight) pueden alcanzar un nivel de calidad aceptable en la tarea de resumen clínico en español, comparados con modelos frontier de nube (Claude Opus), bajo los requisitos de **privacidad de datos** y **sostenibilidad de costos** de un entorno clínico real.

### 1.4 Restricciones No Negociables

| Restricción | Justificación |
|---|---|
| **Privacidad de datos** | Las historias clínicas contienen datos sensibles que no pueden salir de la infraestructura local. Ningún dato puede enviarse a servicios externos de nube |
| **Costos operativos** | El uso de APIs de modelos comerciales no es sostenible a largo plazo para entornos clínicos de alto volumen. La solución en producción debe ser local |
| **Idioma** | La herramienta opera exclusivamente en español. Todo el pipeline — modelos, datos de entrenamiento y evaluación — debe ser en español |

### 1.5 Roles del Proyecto

| Rol | Responsabilidades |
|---|---|
| **Product Owner (PO)** | Coordinación con médicos, definición de criterios de calidad clínica, revisión de datos de entrenamiento, decisiones de viabilidad |
| **AI Agent (Claude Code)** | Implementación técnica, scripts de evaluación, integración de APIs, fine-tuning, automatización y comparación de modelos |

---

## 2. Fase 1 — Fundamentos Técnicos

> **Construir la base: infraestructura, dataset y pipeline — sin intervención médica**

### 2.1 Objetivo de la Fase

Establecer toda la infraestructura técnica necesaria para que el proyecto pueda ejecutarse de forma reproducible, dockerizada y evaluable. Su entregable principal es el entorno funcional y el dataset base listo para uso programático.

### 2.2 Requerimientos Técnicos

#### Infraestructura y Entorno

Toda la infraestructura debe ser containerizada con **Docker** para garantizar reproducibilidad y portabilidad.

| Componente | Especificación |
|---|---|
| **Contenedores** | Docker + Docker Compose para todos los servicios del proyecto |
| **Inferencia de modelos** | Ollama (modelos locales) + Hugging Face Transformers |
| **Orquestación LLM** | LangChain o LlamaIndex para gestión del pipeline de prompts |
| **Almacenamiento** | AWS S3 para dataset, modelos fine-tuned y outputs de evaluación |
| **Cómputo GPU** | AWS EC2 (`g4dn.xlarge` / `g5.xlarge`) — créditos AWS disponibles para B.2 y B.3 |
| **Lenguaje base** | Python 3.11+ |

#### Herramientas MCP

Se requieren dos integraciones de Model Context Protocol para el desarrollo:

- **MCP para Hugging Face** — gestión de modelos, datasets y Spaces desde el entorno de desarrollo
- **MCP o Skill para Ollama** — pull, run, list e interacción con modelos locales directamente desde el IDE

#### Especificación del Dataset

| Requisito | Descripción |
|---|---|
| **Idioma** | Español exclusivamente |
| **Formato** | Texto libre narrativo, tal como se escribe en la práctica clínica real (no estructurado) |
| **Complejidad** | Mezcla de casos simples y complejos: comorbilidades, polimedicación, evolución a largo plazo |
| **Especialidades** | Diversas: medicina interna, endocrinología, cardiología, neurología, entre otras |
| **Anonimización** | Completa — sin datos que permitan identificar al paciente |
| **Volumen mínimo** | 10 pares HC/Resumen para MVP — recomendado 25-50 pares |

Fuentes en orden de preferencia:

1. HC reales anonimizadas — requiere autorización institucional
2. HC sintéticas creadas por médicos colaboradores basadas en casos típicos
3. HC sintéticas generadas por IA — solo como último recurso, siempre validadas por un médico

### 2.3 Diseño del Prompt Estandarizado

Todos los modelos evaluados reciben el mismo prompt. El sistema instruye al modelo a actuar como médico especialista y generar un Resumen Ejecutivo Técnico con cuatro secciones:

- **Trayectoria Clínica** — secuencia diagnóstica y cambios en el estado clínico
- **Intervenciones Consolidadas** — regímenes farmacológicos con dosis, procedimientos y tolerabilidad
- **Estado de Seguridad** — alergias, contraindicaciones y reacciones adversas
- **Dominios Clínicos Activos** — consolidación por áreas: metabólico, cardiovascular, neurológico, etc.

### 2.4 Pipeline de Evaluación Automatizada

```
1. Cargar dataset de HCs desde JSON/CSV
2. Enviar cada HC al modelo con el prompt estandarizado
3. Capturar y almacenar el output (resumen generado)
4. Calcular métricas automáticas contra el gold standard (ROUGE, BERTScore)
5. Generar tabla comparativa de resultados
```

### 2.5 Entregables de la Fase 1

| Entregable | Descripción |
|---|---|
| **Repositorio dockerizado** | Proyecto completo en contenedores, reproducible en cualquier entorno |
| **Dataset base** | Mínimo 10 HCs anonimizadas en español, formateadas en JSON |
| **Prompt estandarizado** | System prompt + User prompt validados y documentados |
| **Pipeline de evaluación** | Script funcional que procesa cualquier modelo con el dataset |
| **Integración Baseline B.1** | API de Claude Opus 4.6 y Sonnet 4.6 integrada y funcional |

---

## 3. Fase 2 — Evaluación de Modelos

> **Comparar tres categorías de modelos usando métricas objetivas**

### 3.1 Objetivo de la Fase

Ejecutar y comparar las tres categorías de modelos LLM sobre el mismo dataset estandarizado para determinar cuál enfoque produce los mejores resúmenes clínicos en español.

---

### 3.2 Etapa B.1 — Modelos Genéricos Preentrenados `☁️ Cloud`

Sirven como techo de calidad de referencia. **No pueden usarse en producción** por restricciones de privacidad y costo.

| Parámetro | Valor |
|---|---|
| **Modelos** | Claude Opus 4.6, Claude Sonnet 4.6 |
| **Ejecución** | Nube / Remota vía API de Anthropic |
| **Propósito** | Establecer baseline de rendimiento máximo |

---

### 3.3 Etapa B.2 — Modelos Comunitarios Fine-tuned `🖥️ Local`

Modelos ya especializados en dominio médico, disponibles en repositorios públicos. Se descargan y ejecutan localmente.

**Candidatos en Hugging Face:**

| Modelo | Descripción |
|---|---|
| `somosnlp/spanish_medica_llm` | Modelo médico en español |
| `somosnlp/Sam_Diagnostic` | Diagnóstico médico en español |
| `kingabzpro/Qwen-3-32B-Medical-Reasoning` | Qwen 3 (32B) con razonamiento médico |

**Candidatos en Ollama:**

| Modelo | Descripción |
|---|---|
| `medgemma` | Modelo médico de Google entrenado en datos médicos diversos |
| `Qwen3_Medical_GRPO` | Qwen 3 con SFT + GRPO para análisis clínico |
| `meditron` | Llama 2 adaptado al dominio médico |
| `llama3-med42-8b` | LLaMA-3 instruccionado para conocimiento médico |
| `biomistral` | Mistral biomedical preentrenado en PubMed Central |

> ⚠️ **Nota:** La mayoría de los modelos médicos en Ollama están centrados en inglés. Deben evaluarse para rendimiento en español antes del benchmark completo. Los modelos basados en **Qwen** son especialmente prometedores por su soporte multilingüe (29+ idiomas).

---

### 3.4 Etapa B.3 — Fine-tuning Personalizado `🖥️ Local`

Entrenamiento de un modelo open-weight propio usando datasets curados de medicina en español.

| Componente | Detalle |
|---|---|
| **Modelo base candidato** | Qwen 2.5 / Llama 3 / Gemma 2 — seleccionar según rendimiento en B.2 |
| **Técnica de entrenamiento** | LoRA / QLoRA — eficiente en memoria, apto para GPUs de AWS EC2 |
| **Datasets de entrenamiento** | `somosnlp/SMC` y `somosnlp/medical_en_es_formato_chatML_Gemma` |
| **Infraestructura** | AWS EC2 `g4dn.xlarge` o `g5.xlarge` — créditos AWS disponibles |
| **Almacenamiento** | AWS S3 para checkpoints, modelo final y outputs |
| **Exportación** | Formato GGUF para uso con Ollama localmente |

---

### 3.5 Métricas de Evaluación

| Métrica | Tipo | Descripción |
|---|---|---|
| Precisión terminológica | Cualitativa | Uso correcto de terminología médica técnica |
| Completitud de información | Cualitativa | Captura todos los datos clínicamente relevantes |
| Organización cronológica | Cualitativa | Secuencia temporal correcta de eventos clínicos |
| Estructuración por dominios | Cualitativa | Información agrupada por áreas clínicas |
| Calidad del español médico | Cualitativa | Nivel de lenguaje técnico apropiado para médicos |
| Omisión de datos críticos | **Seguridad — crítica** | No omite alertas de seguridad (alergias, contraindicaciones) |
| Utilidad clínica general | Global | ¿El médico usaría este resumen en consulta? |
| ROUGE / BERTScore | Automática | Comparación textual contra gold standard |

### 3.6 Tabla Comparativa de Resultados

| Métrica | B.1 Genérico ☁️ | B.2 Comunitario 🖥️ | B.3 Personalizado 🖥️ |
|---|:---:|:---:|:---:|
| Tipo de ejecución | Nube/API | Local | Local |
| Precisión terminológica | — | — | — |
| Completitud | — | — | — |
| Organización cronológica | — | — | — |
| Calidad del español | — | — | — |
| Omisión de datos críticos | — | — | — |
| Utilidad clínica general | — | — | — |

### 3.7 Entregables de la Fase 2

- Outputs generados por los tres enfoques sobre el dataset estandarizado
- Tabla comparativa completa con métricas automáticas calculadas
- Modelo fine-tuned B.3 exportado y funcionando localmente vía Ollama
- Informe técnico de rendimiento
- Recomendación técnica: modelo candidato para la validación médica de Fase 3

---

## 4. Fase 3 — Validación Clínica

> **Donde la tecnología encuentra al médico — y define si el proyecto es viable**

### 4.1 Objetivo de la Fase

Obtener validación clínica experta para determinar si el mejor modelo identificado en Fase 2 cumple el **umbral de calidad mínimo** para ser útil y seguro en un entorno médico real.

> 💡 El umbral de calidad **no lo define el equipo técnico**. Lo definen los médicos especialistas que revisarán los resúmenes generados.

### 4.2 Proceso de Colaboración Médica

Se reclutarán entre 1 y 3 médicos especialistas como revisores voluntarios:

1. **Presentación del proyecto** — discurso de convencimiento con énfasis en impacto clínico y bajo compromiso de tiempo (10-15 minutos por caso, mínimo 10 casos)
2. **Entrega del material** — pares HC original + resumen generado por el mejor modelo de Fase 2
3. **Recolección de correcciones** — calificaciones mediante la rúbrica estructurada

### 4.3 Incentivos para los Médicos Colaboradores

| Incentivo | Descripción |
|---|---|
| **Reconocimiento profesional** | Figura como Médico Colaborador Experto en el proyecto |
| **Acceso prioritario** | Uso de la herramienta antes de su lanzamiento general |
| **Sin costo** | No hay ninguna contraprestación económica requerida |
| **Bajo compromiso** | 10-15 minutos por caso, sin plazos estrictos, a su ritmo |

### 4.4 Rúbrica de Evaluación Médica (escala 1–5)

| Métrica | 1 — Inaceptable | 3 — Aceptable | 5 — Excelente | Mínimo requerido |
|---|---|---|---|:---:|
| Precisión terminológica | Términos incorrectos | Mayormente correcto | Terminología impecable | ≥ 3.5 |
| Completitud | Omite datos críticos | Captura lo principal | No omite nada | ≥ 3.5 |
| Organización cronológica | Sin orden temporal | Orden general correcto | Cronología perfecta | ≥ 3.5 |
| Estructuración por dominios | Sin estructura | Básicamente correcta | Organización óptima | ≥ 3.5 |
| Calidad del español médico | Lenguaje informal | Aceptable pero mejorable | Español médico ejemplar | ≥ 3.5 |
| Omisión de datos críticos | Omite alertas | Alertas principales presentes | Seguridad cubierta | ≥ 3.5 |
| Utilidad clínica general | No lo usaría | Útil con correcciones | Lo usaría tal cual | ≥ 4.0 |

### 4.5 Umbrales de Calidad

| Parámetro | Valor Sugerido | Valor Definitivo |
|---|:---:|:---:|
| Calificación mínima por métrica individual | ≥ 3.5 / 5 | A definir con médicos |
| Calificación promedio global | ≥ 4.0 / 5 | A definir con médicos |
| Porcentaje de casos "Sí, lo usaría" | ≥ 80% | A definir con médicos |
| Porcentaje "Confiable" o superior | ≥ 75% | A definir con médicos |

---

## 5. Versión 3 — Visión Futura del Producto

> ⚠️ **Alcance futuro — No forma parte del proyecto actual.** Se documenta como hoja de ruta.

### 5.1 El Problema Real que Resuelve la V3

Más allá del resumen clínico, el médico enfrenta un problema de fondo: el tiempo de consulta es limitado, pero la responsabilidad sobre cada paciente es total. Cada minuto que el médico dedica a leer, buscar o recordar información es un minuto que no está con el paciente.

La V3 convierte al Copiloto Clínico en un **asistente activo**, no solo un resumidor pasivo.

---

### 5.2 Funcionalidades Propuestas

#### 🚨 Alertas Proactivas en Tiempo Real

El sistema detecta automáticamente situaciones de riesgo al momento de prescribir:

- _"El paciente ya toma X — agregar Y puede causar Z"_
- _"Con la insuficiencia renal actual, la dosis de este fármaco debe reducirse"_
- _"Este paciente ha descompensado 3 veces en los últimos 6 meses con este esquema"_

**Impacto directo:** decisiones más seguras en menos tiempo.

#### 📋 Preparación Automática de Consulta

Antes de que el médico entre a la consulta, el sistema genera automáticamente:

- Resumen ejecutivo actualizado del paciente
- Pendientes clínicos: exámenes no revisados, seguimientos prometidos
- Preguntas sugeridas basadas en la evolución reciente

**Impacto directo:** el tiempo de preparación pasa de 5-7 minutos a menos de 1 minuto.

#### ✍️ Documentación Asistida Post-Consulta

- El médico dicta o escribe puntos clave
- La IA genera la nota clínica completa en lenguaje médico técnico
- El médico revisa, corrige y firma en segundos

**Impacto directo:** la carga administrativa post-consulta se reduce hasta un 70%.

#### 📊 Análisis Poblacional para el Médico

- _"¿Cuántos de mis pacientes diabéticos han descompensado en los últimos 3 meses?"_
- _"¿Qué esquemas terapéuticos han tenido mejor adherencia en mi consulta?"_
- _"¿Qué pacientes tengo con mayor riesgo cardiovascular que no han venido en más de 6 meses?"_

**Impacto directo:** el médico pasa de reaccionar a situaciones clínicas a anticiparlas.

---

### 5.3 Por Qué la V3 Mejora la Vida del Médico

| Problema Actual | Sin Copiloto V3 | Con Copiloto V3 |
|---|---|---|
| Preparación de consulta | 5-7 min leyendo el expediente completo | < 1 min revisando resumen ejecutivo actualizado |
| Riesgo de omisión | Dependiente de memoria y lectura rápida bajo presión | Alertas proactivas antes de prescribir |
| Documentación post-consulta | 10-15 min escribiendo notas clínicas | 2-3 min revisando y firmando borrador generado por IA |
| Seguimiento de pacientes | Manual, dependiente de agenda y memoria | Identificación automática de pacientes en riesgo |
| Carga cognitiva | Alta — el médico debe recordar y buscar todo | Reducida — la IA tiene la memoria del expediente |

### 5.4 Prerrequisito para la V3

> La Versión 3 **solo es viable** si el modelo local alcanza el umbral de calidad clínica definido en Fase 3. Sin validación médica aprobada, no hay base para construir un asistente activo. El trabajo de las Fases 1, 2 y 3 es exactamente ese prerrequisito.

---

## 6. Plan de Trabajo

| # | Tarea | Descripción | Responsable | Fase |
|:---:|---|---|:---:|:---:|
| 1 | Infraestructura y entorno | Repo dockerizado, Docker Compose, MCPs configurados | AI Agent | Fase 1 |
| 2 | Dataset base | Conseguir/generar HCs anonimizadas en español, formatear en JSON | PO + AI Agent | Fase 1 |
| 3 | Pipeline de evaluación | Script para correr cualquier modelo sobre el dataset y medir métricas | AI Agent | Fase 1 |
| 4 | Baseline B.1 (Claude) | Integrar API Claude Opus/Sonnet, correr dataset, almacenar outputs | AI Agent | Fase 2 |
| 5 | Evaluación B.2 (Comunitario) | Descargar y evaluar modelos médicos de HF/Ollama, filtrar por español | AI Agent | Fase 2 |
| 6 | Fine-tuning B.3 | Seleccionar base model, preparar datos, entrenar con LoRA/QLoRA en AWS | AI Agent + PO | Fase 2 |
| 7 | Reclutamiento médico | Contactar 1-3 médicos especialistas, presentar proyecto y acordar revisión | PO | Fase 3 |
| 8 | Validación clínica | Médicos revisan pares HC/Resumen del mejor modelo, completan rúbrica | PO + Médicos | Fase 3 |
| 9 | Decisión de viabilidad | ¿El modelo local alcanza el umbral? Viable para producción o no | PO | Fase 3 |

---

## 7. Preguntas Abiertas

| # | Pregunta | Notas |
|:---:|---|---|
| 1 | ¿Cómo garantizamos comparación justa entre todos los modelos? | Mismo prompt, mismas HCs, mismas métricas — definir protocolo exacto |
| 2 | ¿Qué modelo base usar para el fine-tuning de B.3? | Depende del rendimiento en B.2 — Qwen 2.5 y Llama 3 son candidatos iniciales |
| 3 | ¿Cómo manejar modelos B.2 centrados en inglés? | Evaluar rendimiento en español primero, descartar los que fallen antes del benchmark completo |
| 4 | ¿Cuánto GPU time de AWS se necesita para el fine-tuning? | Estimar antes de ejecutar para controlar consumo de créditos |
| 5 | ¿Qué sucede si ningún modelo local alcanza el umbral médico? | Documentar la brecha, recomendar timeline de re-evaluación en 12-18 meses |

---

*Copiloto Clínico NLP · Proyecto Técnico v1.0 · 2026*