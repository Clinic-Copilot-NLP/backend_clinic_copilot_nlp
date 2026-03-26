# Clinic Copilot NLP


## Project Purpose

The Clinical Copilot is an artificial intelligence tool designed to **summarize patient medical histories** in a technical, structured, and chronological format, optimized for medical decision-making.

Compare the performance of **three types of LLM approaches** on a specific task: summarizing patient clinical histories for doctors. The summary must use high-quality technical medical language, capture all important information, and be organized chronologically and by clinical domains.

The three model categories to compare:

1. **Generic pre-trained LLMs** (e.g, Claude) — used as-is via API or prompt. `Cloud/Remote`
2. **Community fine-tuned models** — existing medical/Spanish-specialized models from Hugging Face or Ollama. `Local`
3. **Custom fine-tuned model** — our own fine-tuned open-weight model trained on curated clinical data. `Local`

---

## Slide Presentation Transcript

The following is the transcript of a slides presentation used to introduce the project to the general public:

---

### Slide 1 — Project Proposal

**Clinical Co-pilot of Natural Language Processing (NLP)**
*Transforming Medical Records into Intelligent Medical Decisions*

Artificial Intelligence | Healthcare | 2026

---

### Slide 2 — Current Problem

Critical barriers in the medical record system impacting the quality of care.

#### Three Fundamental Challenges

| Challenge | Severity | Description | Impact |
| --- | --- | --- | --- |
| **Clinical Inertia due to Overload** | CRITICAL | The physician spends most of the consultation time reading previous notes, delaying direct interaction with the patient and causing delays in decision-making. | Reduction of effective time with the patient |
| **Information Dispersion** | HIGH | Key milestones such as changes in behavior, allergies, and reasons for decompensation are diluted in lengthy and repetitive paragraphs, hindering their rapid identification. | Difficulty in identifying critical data |
| **Risk of Omission** | SEVERE | The pressure of patient care and rapid reading can lead to overlooking vital subjective observations (e.g., dose intolerance) for treatment adjustment. | Risk to patient safety |

---

### Slide 3 — Project Objectives

#### General Objective

Develop a Clinical Copilot based on NLP (using a Large Language Model) capable of analyzing and synthesizing unstructured text medical histories, transforming them into a standardized **Technical Executive Summary** to optimize medical decision-making.

**Viability Assessment:** Determine whether local open-weight models can achieve acceptable quality on this specialized medical reasoning task — producing technical clinical summaries from unstructured patient histories — compared to frontier cloud models (Claude Opus 4.6 as of today). Cloud models serve as the quality baseline, but **cannot be used in production** due to two hard constraints:

1. **Cost** — Recurring API costs for cloud models are not sustainable for clinical environments processing high volumes of patient records.
2. **Data Privacy** — Patient clinical histories contain sensitive and confidential medical data that must not leave the local infrastructure. All processing must remain on-premises; no data can be sent to external cloud services.

**Quality Threshold:** The acceptable quality level is not solely defined by comparison with frontier models. The **Product Owner** is responsible for gathering metrics, feedback, and clinical criteria from **specialized doctors** who will review the generated summaries. These medical professionals define the quality threshold — the minimum standard a summary must meet to be clinically useful and safe. Frontier model output serves as one reference point, but the ultimate quality bar is set by expert medical review.

The project's ultimate goal is to answer: **Is it viable today to run this task locally at a quality level that meets the threshold defined by medical specialists, or is the gap still too large?** This determines whether the Clinical Copilot can move to production under the required privacy and cost constraints.

#### Specific Objectives

1. **Distillation of Findings** — Filter the medical narrative to extract diagnostic milestones and therapeutic regimens, eliminating administrative noise and focusing on what is clinically relevant. *(Information Noise Reduction)*
2. **Technical Translation** — Converting informal or ambiguous descriptions into precise, coded medical language, facilitating communication among professionals. *(Terminological Standardization)*
3. **Evolutionary Synthesis** — Consolidating information by clinical domains (e.g., Metabolic Status, Cardiovascular Risk) instead of a simple chronology, allowing for visualization of evolution by area. *(Organization by Domains)*

---

### Slide 4 — System Architecture

#### Stage A: Text Ingestion and Processing (NLU)

Uses advanced **Natural Language Understanding (NLU)** architecture to extract medical entities, differentiating between different types of clinical information:

- **Family History** — Differentiates from the patient's family history
- **Current Diagnoses** — Identifies present conditions
- **Active Medications** — Recognizes ongoing treatments
- **Subjective Symptoms** — Captures patient complaints

**Contextual Ability:** The system differentiates, for example, whether a pathology is a family history or a current patient diagnosis, understanding the complex semantic relationships of medical language.

**Processing Layers:**

1. Tokenization — Text Segmentation
2. Entity Recognition — Identification of Medical Terms
3. Relationship Analysis — Connections Between Concepts
4. Coreference Resolution — Pronoun Linking
5. Event Extraction — Identification of Clinical Milestones

Input: Plain Text Medical Records.

#### Stage B.1: Generic Pre-trained LLMs (Baseline) — `Cloud/Remote`

Evaluate commercial/generic foundational models on the clinical summarization task to establish a performance baseline.

- **Models** — Claude Opus and Sonnet
- **Method** — Provide the clinical history via prompt with instructions for summarization.
- **Execution** — Cloud-based, accessed via API.
- **Purpose** — Establish baseline performance to compare against specialized models.

#### Stage B.2: Community Fine-tuned Models — `Local`

Source and evaluate pre-existing fine-tuned models from public LLM repositories (Hugging Face, Ollama) specialized in medical language comprehension — particularly in Spanish.

- **Search** — Identify candidate models already fine-tuned for medical NLP tasks.
- **Benchmark** — Run each model against the same standardized inputs used in Stage B.1.
- **Execution** — Downloaded and run locally.
- **Select** — Choose the best-performing community model.

#### Stage B.3: Custom Fine-tuning — `Local`

Train an open-weight base model with curated medical datasets to produce our own fine-tuned model.

- **Base Model Selection** — Choose an open-weight LLM suitable for fine-tuning (e.g., Llama, Gemma).
- **Curated Datasets** — Medical records and summaries validated by specialists.
- **Training** — Fine-tune the base model on clinical history → summary pairs.
- **Execution** — Trained and run locally.
- **Benchmark** — Evaluate against the same inputs used in Stages B.1 and B.2.

#### Stage B — Comparison

Compare all three model categories side by side using defined metrics to determine which approach delivers the best clinical summarization quality.

#### Stage C: Technical Synthesis Generation (Expected Output)

**Expected Technical Executive Summary:**

- **Clinical Trajectory** — Technical evolution from the first record to the current consultation, showing the progression of the patient's condition over time.
  - Diagnostic Sequence
  - Changes in clinical status
  - Relevant milestones
- **Consolidated Interventions** — Therapeutic changes and their documented results, including medication adjustments, procedures, and patient response.
  - Pharmacological regimens
  - Procedures performed
  - Efficacy and tolerability
- **Safety Status** — Critical alerts detected in the narrative, such as allergies, contraindications, adverse effects, and other risk factors.
  - Documented allergies
  - Contraindications
  - Adverse reactions

---

### Slide 5 — Practical Demonstration

**Important:** This application is designed exclusively for the **Spanish language**. All inputs, outputs, training datasets, and evaluation resources must be in Spanish. The models evaluated in Stages B.2 and B.3 must be trained or fine-tuned using Spanish-language medical corpora.

**Example of the Synthesis Process:**

**Phase 1 — Input:**

> *"En 2023 el paciente vino quejándose de mucha sed a pesar de tomar bastante agua. Le mandaron medicamento para el azúcar pero le cayó mal al estómago. Hace seis meses regresó y dijo que ya no sentía los pies..."*

- Lenguaje informal
- Información dispersa
- Falta de estructura clara

**Phase 2 — Process:**

| Análisis | Texto Original | Interpretación |
| --- | --- | --- |
| Análisis de Síntomas | "mucha sed" | Polidipsia (síntoma de DM) |
| Relación Causa-Efecto | "medicamento... le cayó mal al estómago" | Intolerancia a biguanidas |
| Progresión de Enfermedad | "ya no sentía los pies" | Neuropatía periférica |

**Phase 3 — Output:**

> *"Paciente con diabetes mellitus tipo 2 de larga evolución. Antecedente de intolerancia gastrointestinal a biguanidas. Evidencia de progresión a neuropatía periférica sensitiva en los últimos seis meses."*

- Lenguaje Médico Preciso
- Información Estructurada
- Listo para Toma de Decisiones

**Transformación Completa:** De Narrativa Informal a Documentación Clínica Estandarizada en Segundos

| Métrica | Valor |
| --- | --- |
| Precisión Clínica | 95% |

---

### Slide 6 — The Future of Healthcare

*Artificial Intelligence as an Ally for Healthcare Professionals*

**Enhancing Diagnostic Accuracy and Freeing Up Time for What Matters Most: the Patient**

*Transforming Medicine, One Summary at a Time*

---

## Technical Decisions & Requirements

### Stage B.1 — Generic Pre-trained LLMs (Baseline) `Cloud/Remote`

Use commercial foundational models via API/prompt to establish a performance baseline:

    - Claude Opus 4.6, Claude Sonnet 4.6, etc.

### Stage B.2 — Community Fine-tuned Models `Local`

Source and evaluate existing fine-tuned models from public repositories (**Hugging Face**, **Ollama**) specialized in medical language comprehension in **Spanish**. Downloaded and run locally.

**Candidate Models (Hugging Face):**

- [somosnlp/spanish_medica_llm](https://huggingface.co/somosnlp/spanish_medica_llm)
- [somosnlp/Sam_Diagnostic](https://huggingface.co/somosnlp/Sam_Diagnostic)
- [kingabzpro/Qwen-3-32B-Medical-Reasoning](https://huggingface.co/kingabzpro/Qwen-3-32B-Medical-Reasoning) — Qwen 3 (32B) fine-tuned with medical reasoning dataset (medical-o1-reasoning-SFT)

**Candidate Models (Ollama):**

- [medllama2](https://ollama.com/library/medllama2) — Fine-tuned Llama 2 on MedQA dataset for medical Q&A
- [meditron](https://ollama.com/library/meditron) — Llama 2 adapted to medical domain via medical papers and guidelines
- [llama3-med42-8b](https://ollama.com/thewindmom/llama3-med42-8b) — Clinical LLM built on LLaMA-3, instruction-tuned for medical knowledge
- [medgemma](https://ollama.com/alibayram/medgemma) — Google's medical model trained on diverse medical data
- [medichat-llama3](https://ollama.com/monotykamary/medichat-llama3) — LLaMA-3 fine-tuned on health information datasets
- [Medical-Llama3-8B](https://ollama.com/lazarevtill/Medical-Llama3-8B) — Llama3 8B fine-tuned for medical Q&A
- [Qwen3_Medical_GRPO](https://ollama.com/lastmass/Qwen3_Medical_GRPO) — Qwen 3 fine-tuned with SFT + GRPO for clinical case analysis and medical reasoning
- [biomistral](https://ollama.com/cniongolo/biomistral) — Mistral-based biomedical LLM pre-trained on PubMed Central
- [MedExpert](https://ollama.com/OussamaELALLAM/MedExpert) — Medical expert model for clinical tasks

> **Note:** Most Ollama medical models are English-centric. They must be evaluated for Spanish-language performance, as this application operates exclusively in Spanish. Qwen-based models are particularly promising due to strong multilingual support (29+ languages including Spanish).

### Stage B.3 — Custom Fine-tuning `Local`

Fine-tune an open-weight base model using curated medical datasets. Trained and run locally.

**Candidate Datasets for Fine-tuning:**

- [somosnlp/SMC](https://huggingface.co/datasets/somosnlp/SMC)
- [somosnlp/medical_en_es_formato_chatML_Gemma](https://huggingface.co/datasets/somosnlp/medical_en_es_formato_chatML_Gemma)

### Evaluation Strategy

All three model categories must be evaluated on the **same standardized inputs** and compared using defined metrics. The goal is to demonstrate which approach delivers the best clinical summarization quality for Spanish-language medical records.

**Proposed Comparison Table:**

| Metric | Generic LLM (B.1) | Community Fine-tuned (B.2) | Custom Fine-tuned (B.3) |
| --- | --- | --- | --- |
| Execution type | Cloud/Remote | Local | Local |
| Medical terminology accuracy | — | — | — |
| Information completeness | — | — | — |
| Chronological organization | — | — | — |
| Domain-based structuring | — | — | — |
| Spanish language quality | — | — | — |
| Omission of critical data | — | — | — |
| Overall clinical usefulness | — | — | — |

### Tooling

- No prior experience with the Hugging Face platform — will need assistance.
- **MCP for Hugging Face** — Use an MCP server to manage Hugging Face resources (models, datasets, spaces) as a development tool.
- **MCP or Skill for Ollama** — Use an MCP server or Claude Code skill to manage Ollama models (pull, run, list, interact) directly from the development environment.
- **Docker** — The entire project must be dockerized. All services (model inference, evaluation pipelines, API endpoints) must run in containers to ensure reproducibility, portability, and alignment with the on-premises deployment requirement.

### Desired Result

- A comparative analysis of three model categories on clinical summarization quality.
- Identify which approach produces the best summary: professional, technically precise, chronologically and domain-organized, capturing all important information.
- The summary must use high-quality technical medical language for the doctor.
- **Core need:** Doctors don't always have time to read entire patient clinical histories, risking omission of important information buried within the records.

---

## Work Plan

**Purpose of this document:** Propose a complete work plan for the project covering both the **coding/technical side** and the **human/product side**. Each task includes context, deliverables, and a clear responsible party.

### Roles

| Role | Description |
| --- | --- |
| **Product Owner (PO)** | The human developer and product owner. Responsible for clinical requirements, medical expert coordination, quality threshold definition, and final acceptance. |
| **AI Agent** | The agentic coding AI (Claude Code). Responsible for code implementation, model evaluation scripts, technical research, and automation. |

---

### Task 1 — Define Quality Threshold & Evaluation Criteria

**Responsible:** Product Owner
**Context:** Before any model can be evaluated, the quality bar must be defined. The PO must coordinate with specialized doctors to establish what constitutes a clinically acceptable summary.

- [ ] Recruit 1–3 specialized doctors as reviewers
- [ ] Define evaluation rubric (accuracy, completeness, terminology, safety)
- [ ] Establish minimum acceptance scores per metric
- [ ] Provide 3–5 real or realistic anonymized clinical histories as standardized test inputs (in Spanish)

---

### Task 2 — Prepare Standardized Test Dataset

**Responsible:** Product Owner + AI Agent
**Context:** A common set of clinical history inputs is needed so all three model categories are evaluated on the exact same data.

- [ ] **PO:** Source or create anonymized Spanish-language clinical histories (input)
- [ ] **PO:** Work with doctors to produce gold-standard reference summaries (expected output)
- [ ] **AI Agent:** Format and structure the dataset for programmatic use (JSON/CSV)

---

### Task 3 — Generic LLM Baseline (Stage B.1)

**Responsible:** AI Agent
**Context:** Set up and prompt frontier cloud models (Claude Opus 4.6, Sonnet 4.6) to establish the performance ceiling on the clinical summarization task.

- [ ] Design the summarization prompt (system + user prompt engineering)
- [ ] Implement API integration with Claude models
- [ ] Run all standardized test inputs through the models
- [ ] Collect and store outputs for comparison

---

### Task 4 — Community Model Evaluation (Stage B.2)

**Responsible:** AI Agent
**Context:** Source, download, and evaluate pre-existing fine-tuned models from Hugging Face and Ollama on the same standardized inputs.

- [ ] Set up Hugging Face MCP and Ollama MCP/Skill tooling
- [ ] Pull and configure candidate models (see candidate lists above)
- [ ] Run all standardized test inputs through each candidate model
- [ ] Filter out models with poor Spanish-language performance early
- [ ] Collect and store outputs for comparison

---

### Task 5 — Custom Fine-tuning (Stage B.3)

**Responsible:** AI Agent + Product Owner
**Context:** Fine-tune an open-weight base model on curated Spanish medical data to produce a custom model for this task.

- [ ] **AI Agent:** Research and select base model (e.g., Qwen 2.5/3, Llama, Gemma)
- [ ] **AI Agent:** Prepare training data from candidate datasets (Spanish medical corpora)
- [ ] **PO:** Review and validate training data quality with medical specialists
- [ ] **AI Agent:** Implement fine-tuning pipeline (LoRA/QLoRA)
- [ ] **AI Agent:** Train, export, and run the fine-tuned model locally
- [ ] **AI Agent:** Run standardized test inputs and collect outputs

---

### Task 6 — Comparative Evaluation & Metrics

**Responsible:** AI Agent + Product Owner
**Context:** Compare all three model categories side by side using the metrics and thresholds defined in Task 1.

- [ ] **AI Agent:** Build comparison framework (automated metrics where possible)
- [ ] **PO:** Coordinate doctor review of outputs from all three categories (blind evaluation)
- [ ] **AI Agent:** Compile results into the comparison table
- [ ] **PO:** Validate results against the quality threshold

---

### Task 7 — Viability Decision

**Responsible:** Product Owner
**Context:** Based on the comparative evaluation, determine whether local models meet the quality threshold defined by medical specialists.

- [ ] Review comparison results with medical reviewers
- [ ] Determine if any local model (B.2 or B.3) meets the acceptance threshold
- [ ] Document the viability conclusion: **viable for production** or **not yet viable**
- [ ] If viable: define next steps for productionization
- [ ] If not viable: document the gap and recommend a reassessment timeline

---

### Open Questions

1. **Generic LLM Baseline (Stage B.1)** — How do we set up and prompt generic LLMs (Claude) to establish a fair baseline?
2. **Community Models (Stage B.2)** — How can we evaluate existing fine-tuned models from Hugging Face and Ollama to determine which one best fits this task?
3. **Custom Fine-tuning (Stage B.3)** — What is needed to fine-tune an open-weight model? Do we need a dataset of clinical histories paired with summaries? What base model and training approach should we use?
4. **Metrics & Comparison** — What metrics do we use to compare all three categories? How do we ensure a fair, standardized evaluation across all models?
