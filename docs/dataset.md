# Dataset: somosnlp/SMC (Spanish Medical Corpus)

## Descripcion general

El **Spanish Medical Corpus (SMC)** es un corpus de texto medico en espanol compilado y publicado por [SomosNLP](https://somosnlp.org) en el marco del Hackathon **#Somos600M 2024**. Fue creado con el objetivo de reunir en un solo recurso publico textos clinicos y biomedicos en espanol provenientes de multiples fuentes heterogeneas, facilitando el entrenamiento y la evaluacion de modelos de lenguaje medico en espanol.

- **Organizacion:** SomosNLP
- **Evento:** Hackathon #Somos600M 2024
- **Licencia:** Apache 2.0
- **Enlace:** [https://huggingface.co/datasets/somosnlp/SMC](https://huggingface.co/datasets/somosnlp/SMC)

---

## Tamano y estructura

| Caracteristica     | Valor                        |
|--------------------|------------------------------|
| Total de filas     | 2.140.000 (aprox. 2,14M)     |
| Splits disponibles | 1 (solo `train`)             |
| Tamano comprimido  | ~48 MB                       |
| Idioma principal   | Espanol (ES y CL)            |

### Columnas del dataset

| Columna          | Tipo   | Descripcion                                                                                              |
|------------------|--------|----------------------------------------------------------------------------------------------------------|
| `raw_text`       | string | Texto clinico principal. Es el **input** del sistema: historia clinica, caso clinico, articulo o pregunta |
| `topic`          | string | Diagnostico o tema medico principal del texto. Referencia parcial del output (no es un resumen completo) |
| `speciallity`    | string | Especialidad medica asociada al texto (oncologia, medicina interna, farmacologia, etc.)                  |
| `raw_text_type`  | enum   | Tipo de texto: `clinic_case`, `open_text`, `question`                                                   |
| `topic_type`     | enum   | Tipo de topico: `medical_diagnostic`, `medical_topic`, `answer`, `natural_medicine_topic`, `other`       |
| `source`         | int    | ID numerico de la fuente original (valores del 1 al 13)                                                 |
| `country`        | string | Pais de origen: `es` (Espana) o `cl` (Chile)                                                           |
| `document_id`    | string | Identificador del documento original. El mismo caso puede aparecer multiples veces con distintos `topic` |

---

## Las 13 fuentes del corpus

| ID | Nombre                                    | Tipo de contenido                                   | Pais |
|----|-------------------------------------------|-----------------------------------------------------|------|
| 1  | Cantemist                                 | Casos oncologicos con codigos CIE-O 3               | ES   |
| 2  | MedlinePlus Spanish (NLM)                 | Articulos informativos de salud                     | ES   |
| 3  | PharmaCoNER                               | Texto clinico con entidades farmacologicas anotadas | ES   |
| 4  | Spanish Biomedical Crawled Corpus         | Texto biomedico extraido de la web                  | ES   |
| 5  | CARES                                     | Casos clinicos variados                             | ES   |
| 6  | MEDDOCAN                                  | Registros medicos anonimizados                      | ES   |
| 7  | Enfermedades Wikipedia                    | Articulos de Wikipedia sobre enfermedades           | ES   |
| 8  | BioMistral / BioInstructQA Spanish        | Pares pregunta-respuesta biomedicos                 | CA   |
| 9  | DisTEMIST                                 | Textos con entidades de enfermedad anotadas         | ES   |
| 10 | Chilean Waiting List Corpus               | Registros de listas de espera medica                | CL   |
| 11 | BARR2                                     | Corpus biomedico general                            | ES   |
| 12 | SPACCC                                    | Casos clinicos de UCI                               | ES   |
| 13 | MedLexSp                                  | Lexico medico en espanol                            | ES   |

---

## Relevancia para este proyecto

### Lo que el dataset provee

El SMC provee el **input** del sistema: texto clinico real en espanol. Los registros con `raw_text_type == "clinic_case"` (fuentes 1, 3, 5, 6, 9, 12) contienen historias clinicas estructuradas con secciones como Anamnesis, Exploracion fisica, Diagnostico, Tratamiento y Evolucion. Ese texto es exactamente lo que el endpoint `POST /api/analyze` recibe como `historia_clinica`.

### Lo que el dataset NO provee

El SMC **no provee el output estructurado** que este proyecto genera. La columna `topic` contiene el diagnostico principal (por ejemplo: "Adenocarcinoma de sigma") pero no es un resumen ejecutivo tecnico completo. El output del sistema es un JSON con cuatro secciones sintetizadas:

- Trayectoria clinica
- Intervenciones consolidadas
- Estado de seguridad
- Sintesis tecnica

### El gap

El campo `topic` es un rotulo de clasificacion, no un resumen. No incluye evolucion cronologica, cambios en el tratamiento, alertas de seguridad ni organizacion por dominios clinicos. Eso es exactamente lo que el LLM debe generar a partir del `raw_text`.

Esto implica que el SMC es util para **testear el endpoint con inputs reales**, pero no se puede usar directamente como dataset de entrenamiento supervisado (pares input/output) sin generar los outputs de referencia con modelos de frontera o con revision medica especializada.

---

## Ejemplo real de un registro

El siguiente registro es representativo de los casos clinicos de mejor calidad en el corpus (fuente 1, Cantemist):

```
raw_text:
  "Varón de 69 años que acude a urgencias por rectorragia de 3 semanas de evolución.
   Anamnesis: Paciente con antecedentes de hipertensión arterial en tratamiento con
   enalapril 10mg/día, sin alergias medicamentosas conocidas. Niega tabaquismo y
   consumo de alcohol. Refiere cambio en el ritmo deposicional con heces más blandas
   en los últimos 2 meses y pérdida de 4 kg de peso.
   Exploración física: Abdomen blando y depresible, con masa palpable en fosa ilíaca
   izquierda. Tacto rectal: sangre roja en guante.
   Pruebas complementarias: Colonoscopia — masa vegetante en sigma. Biopsia:
   adenocarcinoma moderadamente diferenciado. TC abdominopélvica: tumor de sigma
   sin adenopatías ni metástasis a distancia.
   Diagnóstico: Adenocarcinoma de sigma estadio II (T3N0M0).
   Tratamiento: Sigmoidectomía laparoscópica con anastomosis colorrectal.
   Evolución: Postoperatorio sin complicaciones. Alta hospitalaria al 5.° día."

topic:        "Adenocarcinoma de sigma"
speciallity:  "Oncología"
raw_text_type: "clinic_case"
topic_type:   "medical_diagnostic"
source:       1
country:      "es"
document_id:  "cantemist-case-00472"
```

---

## Estrategia de uso en el proyecto

### Rol del dataset en el pipeline

El campo `raw_text` es el valor que se pasa directamente al campo `historia_clinica` del body del request `POST /api/analyze`. No requiere transformacion adicional.

### Filtros recomendados para samplear casos de calidad

Aplicar estos filtros antes de usar registros para testing o evaluacion:

```python
df_filtered = df[
    (df["raw_text_type"] == "clinic_case") &
    (df["country"] == "es") &
    (df["raw_text"].str.len() > 500)
]
df_deduped = df_filtered.drop_duplicates(subset="document_id")
```

| Filtro                              | Razon                                                                   |
|-------------------------------------|-------------------------------------------------------------------------|
| `raw_text_type == "clinic_case"`    | Descarta articulos informativos y preguntas — solo casos reales         |
| `country == "es"`                   | Prioriza terminologia medica espanola estandar                          |
| `len(raw_text) > 500`               | Descarta fragmentos demasiado cortos para generar un resumen util       |
| `drop_duplicates(subset="document_id")` | Un documento puede aparecer N veces con distintos `topic`. Usar solo uno |

### Fuentes recomendadas para testing

| ID | Fuente       | Motivo                                                              |
|----|--------------|---------------------------------------------------------------------|
| 1  | Cantemist    | Casos oncologicos completos con todas las secciones clinicas        |
| 5  | CARES        | Variedad de especialidades, formato estandar de caso clinico        |
| 12 | SPACCC       | Casos de UCI con alta densidad de informacion clinica critica       |

### Fuentes a evitar para testing del endpoint

| ID | Fuente              | Motivo                                                              |
|----|---------------------|---------------------------------------------------------------------|
| 2  | MedlinePlus         | Son articulos informativos, no historias clinicas de pacientes      |
| 8  | BioInstructQA       | Formato pregunta-respuesta, incompatible con el input del sistema   |
| 13 | MedLexSp            | Lexico y definiciones, no texto clinico narrative                   |

### Tamano recomendado de muestra

Para validar el endpoint `POST /api/analyze` en fase de desarrollo, se recomienda una muestra de **50 a 100 casos unicos** (post-deduplicacion). Ese tamano es suficiente para detectar fallos de parsing, errores de estructura JSON y degradacion en la calidad del output sin incurrir en costos elevados de API.

---

## Advertencia sobre duplicados

El campo `document_id` identifica el documento fuente original. **El mismo documento puede aparecer multiples veces en el dataset** con distintos valores de `topic`, porque un caso clinico puede tener varios diagnosticos asociados y cada uno genera una fila separada.

Si se samplea sin deduplicar, el mismo texto clinico puede aparecer varias veces en la muestra, sesgando los resultados de evaluacion y generando costos de API innecesarios.

**Siempre deduplicar por `document_id` antes de cualquier sampleo.**

```python
# Correcto
df_sample = df_filtered.drop_duplicates(subset="document_id").sample(n=100, random_state=42)

# Incorrecto — puede incluir el mismo texto multiples veces
df_sample = df_filtered.sample(n=100, random_state=42)
```

---

## Enlace al dataset

[https://huggingface.co/datasets/somosnlp/SMC](https://huggingface.co/datasets/somosnlp/SMC)

---

## Casos de prueba incluidos

Estos casos fueron seleccionados y creados para validar el endpoint `POST /api/analyze` con historias clinicas representativas de distintas especialidades. Cada archivo tiene el formato que el endpoint espera como input.

| Archivo       | Especialidad    | Paciente (edad/sexo) | Condiciones principales                                                        | Complejidad |
|---------------|-----------------|----------------------|--------------------------------------------------------------------------------|-------------|
| `tc_001.json` | Cardiologia     | 71 anos, masculino   | HTA, ICC-FEr (FEVI 32%), fibrilacion auricular cronica, descompensacion aguda  | Alta        |
| `tc_002.json` | Endocrinologia  | 58 anos, femenino    | DM2 de 14 anos, obesidad grado II, neuropatia periferica, retinopatia NPDR     | Alta        |
| `tc_003.json` | Neurologia      | 65 anos, masculino   | Post-ACV isquemico silviano anterior izquierdo, fibrilacion auricular, afasia  | Alta        |
| `tc_004.json` | Nefrologia      | 72 anos, masculino   | ERC G4 diabetica en progresion, anemia renal, HPT secundario, acidosis         | Muy alta    |
| `tc_005.json` | Neumologia      | 68 anos, masculino   | EPOC GOLD III (FEV1 38%), cor pulmonale, oxigenoterapia cronica, exacerbador   | Alta        |

### Formato de cada archivo

Cada archivo JSON sigue este esquema:

```json
{
  "id": "tc_001",
  "especialidad": "cardiología",
  "historia_clinica": "...",
  "nota": "descripción breve del caso"
}
```

El campo `historia_clinica` contiene el texto completo de la historia clinica. Es exactamente el valor que debe enviarse en el campo `historia_clinica` del body del request `POST /api/analyze`.

### Como usar los casos de prueba

```bash
# Leer la historia clínica del caso y enviarla al API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"historia_clinica\": $(cat data/test_cases/tc_001.json | python3 -c \"import sys,json; print(json.dumps(json.load(sys.stdin)['historia_clinica']))\")}"
```

Reemplazar `tc_001.json` por cualquiera de los cinco archivos para probar distintas especialidades.

> El campo `historia_clinica` de cada JSON es exactamente lo que va en el body del request. No es necesario enviar los demas campos (`id`, `especialidad`, `nota`) al endpoint: son metadatos del caso de prueba, no parte del input del sistema.
