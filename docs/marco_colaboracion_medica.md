# Marco de Colaboración Médica

## Definición del Umbral de Calidad y Criterios de Evaluación

---

## 1. Introducción del Proyecto

### ¿Qué es el Copiloto Clínico?

El Copiloto Clínico es una herramienta de inteligencia artificial diseñada para **resumir historias clínicas de pacientes** en un formato técnico, estructurado y cronológico, optimizado para la toma de decisiones médicas.

### ¿Por qué existe este proyecto?

Los médicos enfrentan tres barreras críticas en su práctica diaria:

| Problema | Impacto |
| --- | --- |
| **Inercia clínica por sobrecarga** | El médico dedica la mayor parte de la consulta a leer notas previas, retrasando la interacción directa con el paciente |
| **Dispersión de información** | Hitos clave (cambios de conducta, alergias, motivos de descompensación) se diluyen en párrafos extensos y repetitivos |
| **Riesgo de omisión** | La presión asistencial puede llevar a pasar por alto observaciones vitales para el ajuste terapéutico |

### ¿Qué produce el Copiloto?

A partir de una historia clínica en texto libre, genera un **Resumen Ejecutivo Técnico** estructurado en:

- **Trayectoria Clínica** — Evolución técnica desde el primer registro hasta la consulta actual
- **Intervenciones Consolidadas** — Cambios terapéuticos y sus resultados documentados
- **Estado de Seguridad** — Alertas críticas: alergias, contraindicaciones, reacciones adversas

### ¿Por qué necesitamos a los médicos?

La inteligencia artificial puede generar resúmenes, pero **solo un médico especialista puede determinar si un resumen es clínicamente útil y seguro**. Sin la validación médica, no hay forma de saber si la herramienta está lista para uso real.

El objetivo de esta colaboración es construir un **conjunto de referencia validado por expertos** que defina el estándar de calidad mínimo aceptable.

---

## 2. Discurso de Convencimiento

> **Guía para presentar el proyecto a médicos y solicitar su colaboración voluntaria.**

### Guion Sugerido

---

*"Doctor(a), gracias por su tiempo. Le presento brevemente un proyecto de inteligencia artificial aplicada a la medicina que creemos puede tener un impacto directo en su práctica diaria.*

*Sabemos que uno de los mayores retos en la consulta es el tiempo que se invierte leyendo historias clínicas extensas antes de poder interactuar con el paciente. Información importante — alergias, cambios de medicación, evolución de síntomas — muchas veces queda enterrada en párrafos largos y repetitivos. Y bajo la presión del día a día, existe un riesgo real de pasar por alto datos críticos.*

*Estamos desarrollando un Copiloto Clínico: una herramienta que lee la historia clínica completa del paciente y genera un resumen técnico estructurado — con trayectoria clínica, intervenciones consolidadas y alertas de seguridad — listo para que el médico lo revise en segundos en lugar de minutos.*

*Pero aquí está lo importante: **la inteligencia artificial no puede definir qué es un buen resumen clínico. Solo usted puede hacerlo.***

*Lo que le pedimos es lo siguiente: le presentaremos historias clínicas junto con los resúmenes que genera la IA. Su tarea sería revisar cada par — la historia original y el resumen propuesto — y marcar lo que esté bien, lo que falte, lo que sobre, y lo que esté mal interpretado.*

*No le tomará más de 10-15 minutos por caso, y necesitamos al menos 10 casos revisados, aunque mientras más tengamos, mejor será la herramienta. Su retroalimentación directamente define el estándar de calidad que la IA debe alcanzar.*

*No hay costo alguno para usted. A cambio, su nombre figurará como **médico colaborador experto** en el proyecto, y tendrá acceso prioritario a la herramienta cuando esté lista. Además, estará contribuyendo a una solución que puede ahorrarle tiempo real en cada consulta futura.*

*¿Le interesaría participar?"*

---

### Puntos Clave del Discurso

| Elemento | Propósito |
| --- | --- |
| Empatía con el problema | El médico se identifica con la sobrecarga de información |
| Solución tangible | Se describe el producto de forma concreta y útil |
| El médico define la calidad | Posiciona al doctor como experto indispensable, no como sujeto de prueba |
| Bajo compromiso de tiempo | 10-15 minutos por caso, mínimo 10 casos |
| Sin costo | Elimina la barrera económica |
| Reconocimiento profesional | Incentivo no monetario: crédito como colaborador experto |
| Acceso prioritario | Beneficio directo: usar la herramienta antes que nadie |

### Adaptaciones según contexto

- **Si el médico tiene poco tiempo:** Enfatizar que puede revisar los casos en cualquier momento, a su ritmo, sin plazos estrictos.
- **Si el médico es escéptico sobre IA:** Enfatizar que precisamente por eso necesitamos su ojo clínico — para que la IA no cometa errores.
- **Si el médico pregunta por privacidad:** Todas las historias clínicas utilizadas están completamente anonimizadas. No se utiliza información real de pacientes identificables.

---

## 3. Estrategia de Recopilación de Historias Clínicas

### Fuentes de Historias Clínicas

Las historias clínicas (HC) pueden provenir de las siguientes fuentes, en orden de preferencia:

1. **HC reales anonimizadas** — Historias de pacientes reales con todos los datos identificativos eliminados (nombre, cédula, dirección, teléfono, etc.). Requiere autorización institucional.
2. **HC sintéticas realistas** — Generadas por médicos colaboradores basándose en casos típicos de su práctica, sin corresponder a ningún paciente real específico.
3. **HC sintéticas generadas por IA** — Como último recurso, generadas por Claude Opus 4.6 simulando casos clínicos realistas, pero **siempre validadas por un médico** antes de incluirlas en el dataset.

### Requisitos de las Historias Clínicas

| Requisito | Descripción |
| --- | --- |
| **Idioma** | Español exclusivamente |
| **Extensión** | Variada — desde consultas breves hasta historiales extensos con múltiples visitas |
| **Complejidad** | Mezcla de casos simples y complejos (comorbilidades, polimedicación, evolución a largo plazo) |
| **Especialidades** | Preferiblemente diversas: medicina interna, endocrinología, cardiología, neurología, etc. |
| **Formato** | Texto libre, tal como se encuentra en la práctica real (narrativo, no estructurado) |
| **Anonimización** | Completa — sin datos que permitan identificar al paciente |

### Cantidad Objetivo

| Nivel | Cantidad de pares HC/Resumen | Uso |
| --- | --- | --- |
| **Mínimo viable** | 10 pares | Suficiente para establecer un umbral de calidad inicial |
| **Recomendado** | 25-50 pares | Permite mayor confianza estadística y cubrir más variabilidad |
| **Ideal** | 100+ pares | Dataset robusto para evaluación y potencial entrenamiento |

> **Nota:** Cada par consiste en una historia clínica original + su resumen generado por IA + las correcciones del médico.

---

## 4. Proceso de Generación de Resúmenes con IA

### Modelo Utilizado

**Claude Opus 4.6** (Anthropic) — modelo de lenguaje de frontera, utilizado vía API como línea base de calidad máxima.

### Estrategia de Prompting

El modelo recibe instrucciones para actuar como un médico especialista que debe generar un Resumen Ejecutivo Técnico a partir de la historia clínica proporcionada.

#### Prompt del Sistema (System Prompt)

```
Eres un médico especialista con amplia experiencia clínica. Tu tarea es analizar la
historia clínica proporcionada y generar un Resumen Ejecutivo Técnico siguiendo
estrictamente el formato indicado.

Debes:
- Utilizar lenguaje médico técnico y preciso
- Traducir descripciones informales a terminología médica estandarizada
- Capturar TODA la información clínicamente relevante sin omisiones
- Organizar la información de forma cronológica y por dominios clínicos
- Identificar y destacar alertas de seguridad
- Ignorar información administrativa irrelevante (datos de citas, firmas, etc.)

Formato de salida obligatorio:

## Resumen Ejecutivo Técnico

### 1. Trayectoria Clínica
Evolución técnica desde el primer registro hasta la consulta actual.
- Secuencia diagnóstica
- Cambios en el estado clínico
- Hitos relevantes

### 2. Intervenciones Consolidadas
Cambios terapéuticos y sus resultados documentados.
- Regímenes farmacológicos (con dosis y posología cuando estén disponibles)
- Procedimientos realizados
- Eficacia y tolerabilidad documentada

### 3. Estado de Seguridad
Alertas críticas detectadas en la narrativa.
- Alergias documentadas
- Contraindicaciones identificadas
- Reacciones adversas registradas

### 4. Dominios Clínicos Activos
Consolidación por áreas clínicas (ej: Estado Metabólico, Riesgo Cardiovascular,
Salud Mental, etc.) mostrando la evolución en cada dominio.
```

#### Prompt del Usuario (User Prompt)

```
Analiza la siguiente historia clínica y genera el Resumen Ejecutivo Técnico
según el formato indicado en tus instrucciones.

Historia Clínica:
---
{TEXTO_DE_LA_HISTORIA_CLINICA}
---
```

### Flujo de Generación

```
HC Original (texto libre)
        │
        ▼
  Claude Opus 4.6
  (System + User Prompt)
        │
        ▼
  Resumen Ejecutivo Técnico
  (formato estructurado)
        │
        ▼
  Par [HC Original + Resumen IA]
  listo para revisión médica
```

---

## 5. Formato de Evaluación Médica

### Presentación al Médico

Cada caso se presenta al médico como un **par lado a lado**:

| Columna Izquierda | Columna Derecha |
| --- | --- |
| **Historia Clínica Original** | **Resumen Generado por IA** |
| Texto completo tal como fue escrito | Resumen Ejecutivo Técnico estructurado |

### Plantilla de Corrección

Para cada par HC/Resumen, el médico debe completar:

#### A. Correcciones Específicas

El médico marca directamente sobre el resumen:

| Tipo de Error | Instrucción para el Médico | Ejemplo |
| --- | --- | --- |
| **Información faltante** | Marcar qué dato relevante de la HC no aparece en el resumen | "Falta mencionar antecedente de hipotiroidismo diagnosticado en 2021" |
| **Terminología incorrecta** | Corregir el término médico utilizado | "No es 'neuropatía sensitiva', es 'polineuropatía diabética distal'" |
| **Interpretación errónea** | Señalar donde la IA malinterpretó la información | "La metformina no fue suspendida por intolerancia, fue por insuficiencia renal" |
| **Información innecesaria** | Indicar datos incluidos que no son clínicamente relevantes | "El dato de que el paciente vive solo no es relevante para este resumen" |
| **Error de cronología** | Corregir secuencia temporal incorrecta | "La cirugía fue en 2022, no en 2023" |
| **Resumen ideal** | Reescribir la sección como debería quedar (opcional pero muy valioso) | El médico escribe su versión corregida |

#### B. Rúbrica de Calificación

El médico califica cada métrica en una escala de 1 a 5:

| Métrica | 1 (Inaceptable) | 2 (Deficiente) | 3 (Aceptable) | 4 (Bueno) | 5 (Excelente) | Calificación |
| --- | --- | --- | --- | --- | --- | --- |
| **Precisión terminológica** | Términos incorrectos o confusos | Varios errores de terminología | Mayormente correcto, algunos imprecisos | Preciso con mínimos ajustes | Terminología impecable | ___ |
| **Completitud de información** | Omite datos críticos | Faltan varios datos relevantes | Captura lo principal, faltan detalles | Casi completo | No omite nada relevante | ___ |
| **Organización cronológica** | Sin orden temporal | Cronología confusa | Orden general correcto, algunos saltos | Bien organizado | Cronología perfecta | ___ |
| **Estructuración por dominios** | Sin estructura por áreas | Dominios mal agrupados | Estructura básica correcta | Bien organizado por dominios | Organización clínica óptima | ___ |
| **Calidad del español médico** | Lenguaje informal o incorrecto | Mezcla de registros | Aceptable pero mejorable | Lenguaje técnico apropiado | Español médico ejemplar | ___ |
| **Omisión de datos críticos** | Omite alertas de seguridad | Faltan datos de seguridad | Alertas principales presentes | Casi todas las alertas | Seguridad completamente cubierta | ___ |
| **Utilidad clínica general** | No usaría este resumen | Necesita reescritura mayor | Útil con correcciones | Útil con ajustes menores | Lo usaría tal cual | ___ |

#### C. Evaluación Global

```
¿Usaría este resumen como punto de partida en su consulta?  [ ] Sí  [ ] No

¿Qué tan confiable le parece la información del resumen?
[ ] Nada confiable  [ ] Poco confiable  [ ] Moderadamente confiable  [ ] Confiable  [ ] Muy confiable

Comentarios adicionales (texto libre):
_______________________________________________
_______________________________________________
```

---

## 6. Definición del Umbral de Calidad

### ¿Cómo se construye el estándar de referencia?

```
HC Original + Resumen IA
        │
        ▼
  Revisión del Médico
  (correcciones + calificaciones)
        │
        ▼
  Resumen Corregido = Referencia Gold Standard
        │
        ▼
  Umbral de Calidad = Promedio mínimo aceptable
  definido por las calificaciones de los médicos
```

### Proceso de Validación

1. **Generación:** Claude Opus 4.6 genera el resumen a partir de cada HC
2. **Revisión individual:** Cada médico revisa los pares HC/Resumen de forma independiente
3. **Corrección:** El médico marca errores y reescribe secciones cuando sea necesario
4. **Calificación:** El médico completa la rúbrica de calificación para cada par
5. **Consolidación:** Se recopilan todas las correcciones y calificaciones

### Criterios de Consenso (si hay múltiples revisores)

- Si **2+ médicos** revisan el mismo caso, se consolidan las correcciones:
  - Correcciones en las que todos coinciden → se aplican directamente
  - Correcciones divergentes → se discuten entre revisores o se aplica el criterio más conservador (priorizar seguridad del paciente)
- La calificación final por métrica es el **promedio** de las calificaciones individuales

### Definición del Umbral Mínimo Aceptable

El Product Owner, en conjunto con los médicos colaboradores, debe definir:

| Parámetro | Valor sugerido | Valor definitivo (a definir) |
| --- | --- | --- |
| Calificación mínima por métrica individual | ≥ 3.5 / 5 | ___ |
| Calificación mínima promedio global | ≥ 4.0 / 5 | ___ |
| Porcentaje de casos con "Sí, lo usaría" | ≥ 80% | ___ |
| Porcentaje de casos "Confiable" o superior | ≥ 75% | ___ |

> **Importante:** Estos valores son sugerencias iniciales. Los umbrales definitivos deben ser establecidos por los médicos colaboradores, no por el equipo técnico.

### Resultado: Dataset de Referencia

Al completar este proceso, se obtiene:

| Componente | Descripción |
| --- | --- |
| **HC originales** | N historias clínicas anonimizadas en español |
| **Resúmenes IA** | N resúmenes generados por Claude Opus 4.6 |
| **Correcciones médicas** | Marcas de error, correcciones y reescrituras por cada par |
| **Resúmenes gold standard** | Versiones finales validadas por médicos (resumen IA + correcciones aplicadas) |
| **Calificaciones** | Rúbrica completada por cada médico para cada par |
| **Umbral de calidad** | Valores mínimos aceptables por métrica |

Este dataset es la **piedra angular** de todo el proyecto. Sin él, no es posible evaluar ni comparar las tres categorías de modelos (B.1, B.2, B.3).

---

## 7. Próximos Pasos

Una vez completada la colaboración médica y construido el dataset de referencia:

1. **Formatear el dataset** — Estructurar los pares HC/Resumen validados en formato programático (JSON) para uso automatizado en evaluación
2. **Evaluar modelos genéricos (Etapa B.1)** — Ejecutar las mismas HC a través de Claude Opus 4.6 y Sonnet 4.6 con el prompt estandarizado y comparar contra el gold standard
3. **Evaluar modelos comunitarios (Etapa B.2)** — Probar modelos fine-tuned de Hugging Face y Ollama contra el mismo dataset
4. **Fine-tuning personalizado (Etapa B.3)** — Entrenar un modelo propio usando los pares validados como parte del dataset de entrenamiento
5. **Comparación final** — Tabla comparativa de las tres categorías usando las mismas métricas de la rúbrica médica
6. **Decisión de viabilidad** — ¿Pueden los modelos locales alcanzar el umbral de calidad definido por los médicos?

---

## Anexo: Checklist para el Product Owner

### Antes de contactar médicos
- [ ] Preparar al menos 3 historias clínicas anonimizadas de ejemplo
- [ ] Generar los resúmenes de ejemplo con Claude Opus 4.6
- [ ] Imprimir o preparar digitalmente los pares HC/Resumen para mostrar en la primera reunión
- [ ] Tener lista la plantilla de corrección (Sección 5)

### Durante la reunión con el médico
- [ ] Presentar el discurso de convencimiento (Sección 2)
- [ ] Mostrar un ejemplo concreto de par HC/Resumen
- [ ] Explicar la plantilla de corrección
- [ ] Acordar formato de entrega (papel, documento digital, formulario online)
- [ ] Acordar plazo flexible de entrega
- [ ] Obtener consentimiento de participación

### Después de la reunión
- [ ] Enviar las HC y resúmenes al médico en el formato acordado
- [ ] Dar seguimiento sin presión
- [ ] Recopilar las correcciones y calificaciones
- [ ] Agradecer y confirmar el reconocimiento como colaborador experto

### Al completar las revisiones
- [ ] Consolidar todas las correcciones en el dataset
- [ ] Calcular promedios de calificación por métrica
- [ ] Definir umbrales de calidad definitivos con los médicos
- [ ] Documentar el dataset de referencia final
