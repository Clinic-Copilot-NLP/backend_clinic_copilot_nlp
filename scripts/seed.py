"""
Script de seed para insertar datos de prueba en la base de datos.

Inserta 6 pacientes de demostración con sus análisis clínicos.
Es idempotente: si ya existen pacientes, no hace nada.

Usa SQLAlchemy síncrono con psycopg (no asyncpg) ya que se ejecuta
como script standalone antes de que la app async inicie.

Ejecutar:
    python scripts/seed.py
"""

import json
import logging
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Asegurar que el paquete `app` sea importable desde el directorio raíz
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Namespace estable para UUIDs deterministas
# ---------------------------------------------------------------------------
_NS = uuid.UUID("12345678-1234-5678-1234-567812345678")


def _uid(name: str) -> uuid.UUID:
    """Genera un UUID determinista a partir de un nombre."""
    return uuid.uuid5(_NS, name)


# ---------------------------------------------------------------------------
# Helpers para construir items estructurados
# ---------------------------------------------------------------------------


def _domain(key: str, title: str, status: str, description: str) -> dict:
    return {"id": str(_uid(key)), "title": title, "status": status, "description": description}


def _alert(key: str, title: str, status: str, description: str) -> dict:
    return {"id": str(_uid(key)), "title": title, "status": status, "description": description}


def _timeline(key: str, date: str, title: str, description: str, is_critical: bool) -> dict:
    return {
        "id": str(_uid(key)),
        "date": date,
        "title": title,
        "description": description,
        "is_critical": is_critical,
    }


# ---------------------------------------------------------------------------
# Datos de pacientes y análisis
# ---------------------------------------------------------------------------

PATIENTS_DATA: list[dict] = [
    # ------------------------------------------------------------------
    # 1. María González — Endocrinología
    # ------------------------------------------------------------------
    {
        "patient": {
            "id": _uid("patient-maria-gonzalez"),
            "name": "María González",
            "age": 58,
            "gender": "Femenino",
            "specialty": "Endocrinología",
        },
        "analysis": {
            "id": _uid("analysis-maria-gonzalez"),
            "domains": [
                _domain(
                    "maria-dm2",
                    "Control Metabólico DM2",
                    "warn",
                    "HbA1c actual 7,9% con objetivo < 7,5%. Glucemia en ayunas promedio 148 mg/dL. "
                    "Tratamiento con metformina 2.000 mg/día + liraglutida 1,2 mg/día. "
                    "Control subóptimo persistente a pesar de intensificación farmacológica.",
                ),
                _domain(
                    "maria-neuropatia",
                    "Neuropatía Periférica Diabética",
                    "warn",
                    "Polineuropatía sensitiva en guante y calcetín bilateral diagnosticada hace 3 años. "
                    "Síntomas: parestesias, ardor nocturno y calambres en pies. "
                    "Pregabalina 75 mg/12h con respuesta parcial. Sin úlceras activas.",
                ),
                _domain(
                    "maria-retinopatia",
                    "Retinopatía Diabética",
                    "warn",
                    "Retinopatía diabética no proliferativa (RDNP) leve bilateral diagnosticada hace 8 meses. "
                    "Sin edema macular. Control oftalmológico anual planificado.",
                ),
                _domain(
                    "maria-renal",
                    "Función Renal",
                    "ok",
                    "TFGe 68 mL/min/1,73m². Microalbuminuria 38 mg/g de creatinina. "
                    "Estadio G2A2 de ERC diabética. Nefroprotección con losartán 100 mg/día.",
                ),
                _domain(
                    "maria-peso",
                    "Control de Peso y Obesidad",
                    "warn",
                    "Obesidad grado II (IMC 36,4 kg/m², peso 94 kg). "
                    "Pérdida de 6 kg desde inicio de liraglutida hace 2 años. "
                    "Plan alimentario hipocalórico y actividad física regular recomendados.",
                ),
            ],
            "alerts": [
                _alert(
                    "maria-alert-hba1c",
                    "HbA1c fuera de objetivo",
                    "warn",
                    "HbA1c 7,9% (objetivo < 7,5%). Evaluar intensificación con insulina basal "
                    "o cambio a agonista GLP-1 de mayor potencia (semaglutida).",
                ),
                _alert(
                    "maria-alert-pie",
                    "Riesgo Pie Diabético Categoría 2",
                    "warn",
                    "Neuropatía confirmada sin enfermedad vascular periférica. "
                    "Revisión podológica cada 3-4 meses. Educación sobre cuidado del pie.",
                ),
                _alert(
                    "maria-alert-renal",
                    "Microalbuminuria persistente",
                    "warn",
                    "Microalbuminuria 38 mg/g sugiere inicio de nefropatía diabética. "
                    "Control semestral de función renal y ajuste de IECA/ARA-II.",
                ),
            ],
            "timeline": [
                _timeline(
                    "maria-tl-dx",
                    "2010-03-15",
                    "Diagnóstico DM2",
                    "Diagnóstico de diabetes mellitus tipo 2 a los 44 años. Inicio de metformina 500 mg/día.",
                    False,
                ),
                _timeline(
                    "maria-tl-metformina",
                    "2012-06-01",
                    "Optimización Metformina",
                    "Incremento progresivo de metformina hasta 2.000 mg/día. HbA1c 8,6% al momento del ajuste.",
                    False,
                ),
                _timeline(
                    "maria-tl-sitagliptina",
                    "2019-09-10",
                    "Inicio iDPP-4",
                    "Adición de sitagliptina 100 mg/día por HbA1c persistente sobre 9%. HbA1c 9,2%.",
                    False,
                ),
                _timeline(
                    "maria-tl-glp1",
                    "2022-01-20",
                    "Inicio Liraglutida (GLP-1)",
                    "Incorporación de liraglutida 1,2 mg/día SC por HbA1c 9,4%. Pérdida ponderal de 6 kg en 8 meses.",
                    False,
                ),
                _timeline(
                    "maria-tl-neuropatia",
                    "2022-08-05",
                    "Diagnóstico Neuropatía Periférica",
                    "Electroneurografía confirma polineuropatía sensitiva distal bilateral. Inicio pregabalina.",
                    True,
                ),
                _timeline(
                    "maria-tl-retinopatia",
                    "2024-06-12",
                    "Diagnóstico Retinopatía NPDR",
                    "Fondo de ojo: microaneurismas y exudados duros compatibles con RDNP leve. Control anual.",
                    True,
                ),
            ],
        },
    },
    # ------------------------------------------------------------------
    # 2. Carlos Ramírez — Cardiología
    # ------------------------------------------------------------------
    {
        "patient": {
            "id": _uid("patient-carlos-ramirez"),
            "name": "Carlos Ramírez",
            "age": 71,
            "gender": "Masculino",
            "specialty": "Cardiología",
        },
        "analysis": {
            "id": _uid("analysis-carlos-ramirez"),
            "domains": [
                _domain(
                    "carlos-icc",
                    "Insuficiencia Cardíaca (ICC-FEr)",
                    "danger",
                    "FEVI 32% por ecocardiografía. Internación actual por descompensación aguda: "
                    "disnea de mínimos esfuerzos, ortopnea 3 almohadas, edemas con fóvea hasta rodillas. "
                    "BNP 1.840 pg/mL. Clasificación NYHA III al alta.",
                ),
                _domain(
                    "carlos-hta",
                    "Hipertensión Arterial",
                    "warn",
                    "HTA esencial de 18 años de evolución. PA ingreso 165/95 mmHg a pesar de "
                    "enalapril 10 mg/día y amlodipina 5 mg/día. Requiere optimización antihipertensiva.",
                ),
                _domain(
                    "carlos-fa",
                    "Fibrilación Auricular Crónica",
                    "warn",
                    "FA crónica anticoagulada con rivaroxabán 20 mg/día. FC 98 lpm irregular al ingreso. "
                    "BRIHH preexistente en ECG. Evaluar control de frecuencia cardíaca.",
                ),
                _domain(
                    "carlos-renal",
                    "Función Renal",
                    "warn",
                    "Creatinina 1,4 mg/dL, TFGe 51 mL/min/1,73m². Sodio 133 mEq/L (hiponatremia leve). "
                    "Monitorización estricta durante diuresis forzada.",
                ),
            ],
            "alerts": [
                _alert(
                    "carlos-alert-icc",
                    "Descompensación ICC activa — ingreso urgente",
                    "danger",
                    "Signos clínicos de congestión sistémica y pulmonar grave: BNP 1.840 pg/mL, "
                    "crepitantes bibasales, hepatomegalia 3 cm, SpO2 91% AA. Tratamiento diurético IV.",
                ),
                _alert(
                    "carlos-alert-anticoag",
                    "Anticoagulación activa — riesgo hemorrágico",
                    "warn",
                    "Rivaroxabán 20 mg/día activo. Verificar función renal antes de procedimientos invasivos. "
                    "No suspender sin indicación cardiológica explícita.",
                ),
                _alert(
                    "carlos-alert-hiponatremia",
                    "Hiponatremia dilucional",
                    "warn",
                    "Sodio 133 mEq/L en contexto de descompensación de ICC. "
                    "Restricción hídrica y corrección gradual durante diuresis.",
                ),
                _alert(
                    "carlos-alert-anemia",
                    "Anemia normocítica",
                    "warn",
                    "Hb 11,2 g/dL. Probable anemia de enfermedad crónica en contexto de ICC y ERC estadio 3. "
                    "Descartar déficit de hierro (ferritina, transferrina).",
                ),
            ],
            "timeline": [
                _timeline(
                    "carlos-tl-hta",
                    "2006-01-01",
                    "Diagnóstico HTA",
                    "Diagnóstico de hipertensión arterial esencial. Inicio de enalapril.",
                    False,
                ),
                _timeline(
                    "carlos-tl-fa",
                    "2018-05-14",
                    "Diagnóstico Fibrilación Auricular",
                    "FA crónica detectada en ECG de rutina. Inicio anticoagulación con rivaroxabán.",
                    True,
                ),
                _timeline(
                    "carlos-tl-icc",
                    "2020-09-22",
                    "Diagnóstico ICC-FEr",
                    "Ecocardiograma: FEVI 32%, dilatación VI. Inicio de betabloqueante y IECA. "
                    "Primera internación por descompensación.",
                    True,
                ),
                _timeline(
                    "carlos-tl-dislipemia",
                    "2020-10-01",
                    "Inicio Rosuvastatina",
                    "Dislipemia diagnosticada. Rosuvastatina 10 mg/día. LDL objetivo < 70 mg/dL.",
                    False,
                ),
                _timeline(
                    "carlos-tl-internacion",
                    "2025-01-08",
                    "Internación por Descompensación Aguda ICC",
                    "Segunda descompensación aguda. BNP 1.840 pg/mL, SpO2 91%, edemas hasta rodillas. "
                    "Furosemida IV, ajuste de IECA. Alta en CF NYHA III.",
                    True,
                ),
                _timeline(
                    "carlos-tl-alta",
                    "2025-01-15",
                    "Alta Hospitalaria con Optimización Farmacológica",
                    "Alta con sacubitrilo/valsartán en lugar de enalapril, carvedilol optimizado, "
                    "eplerenona añadida. Control ambulatorio en 2 semanas.",
                    False,
                ),
            ],
        },
    },
    # ------------------------------------------------------------------
    # 3. Ana Martínez — Neurología
    # ------------------------------------------------------------------
    {
        "patient": {
            "id": _uid("patient-ana-martinez"),
            "name": "Ana Martínez",
            "age": 45,
            "gender": "Femenino",
            "specialty": "Neurología",
        },
        "analysis": {
            "id": _uid("analysis-ana-martinez"),
            "domains": [
                _domain(
                    "ana-migrana",
                    "Migraña Crónica",
                    "warn",
                    "Migraña crónica con más de 15 días/mes de cefalea durante 6 meses. "
                    "Aura visual en 40% de episodios. Triptan con respuesta variable. "
                    "Uso excesivo de analgésicos (ibuprofeno > 10 días/mes) — riesgo cefalea por sobreuso.",
                ),
                _domain(
                    "ana-esclerosis",
                    "Posible Esclerosis Múltiple",
                    "danger",
                    "Brote con neuritis óptica derecha y parestesias en MSI (2024). "
                    "RMN cerebral: 3 lesiones hiperintensas en T2/FLAIR periventriculares. "
                    "Pendiente: punción lumbar para bandas oligoclonales y potenciales evocados visuales.",
                ),
                _domain(
                    "ana-ansiedad",
                    "Trastorno de Ansiedad Generalizada",
                    "warn",
                    "Diagnóstico de TAG comórbido con migraña crónica. "
                    "Escitalopram 10 mg/día con respuesta parcial. "
                    "El estrés es factor precipitante identificado de crisis migrañosas.",
                ),
            ],
            "alerts": [
                _alert(
                    "ana-alert-em",
                    "Sospecha de Esclerosis Múltiple — estudio en curso",
                    "danger",
                    "Lesiones desmielinizantes en RMN + brote clínico. Criterios de McDonald parcialmente "
                    "cumplidos. Pendiente punción lumbar y segunda opinión en EM. "
                    "No iniciar inmunomoduladores hasta confirmar diagnóstico.",
                ),
                _alert(
                    "ana-alert-sobreuso",
                    "Cefalea por Sobreuso de Analgésicos",
                    "warn",
                    "Consumo de ibuprofeno > 10 días/mes. Riesgo de cronificación y refractariedad. "
                    "Retirada gradual programada con supervisión neurológica.",
                ),
                _alert(
                    "ana-alert-anticonceptivos",
                    "Contraindicación ACO en Migraña con Aura",
                    "danger",
                    "Migraña con aura + posible EM: contraindicación absoluta de anticonceptivos "
                    "orales combinados por riesgo tromboembólico aumentado. "
                    "Derivación a ginecología para método anticonceptivo alternativo.",
                ),
            ],
            "timeline": [
                _timeline(
                    "ana-tl-migrana",
                    "2015-04-10",
                    "Diagnóstico Migraña Episódica",
                    "Migraña episódica sin aura. Inicio de triptanes (sumatriptán 50 mg) como tratamiento abortivo.",
                    False,
                ),
                _timeline(
                    "ana-tl-cronica",
                    "2019-11-01",
                    "Cronificación Migraña",
                    "Progresión a migraña crónica (>15 días/mes). Inicio de topiramato como profilaxis.",
                    True,
                ),
                _timeline(
                    "ana-tl-ansiedad",
                    "2021-03-15",
                    "Diagnóstico TAG Comórbido",
                    "Trastorno de ansiedad generalizada. Escitalopram 10 mg/día.",
                    False,
                ),
                _timeline(
                    "ana-tl-neuritis",
                    "2024-02-28",
                    "Brote: Neuritis Óptica Derecha",
                    "Pérdida de visión unilateral derecha con dolor ocular. RMN: lesión desmielinizante "
                    "en nervio óptico derecho. Tratamiento con metilprednisolona IV 1 g/día x 3 días.",
                    True,
                ),
                _timeline(
                    "ana-tl-rmn",
                    "2024-03-15",
                    "RMN Cerebral — Lesiones Desmielinizantes",
                    "3 lesiones hiperintensas en T2/FLAIR periventriculares. "
                    "Sospecha de esclerosis múltiple remitente-recurrente.",
                    True,
                ),
                _timeline(
                    "ana-tl-estudio",
                    "2025-01-20",
                    "Estudio diagnóstico EM en curso",
                    "Punción lumbar programada. Potenciales evocados visuales pendientes. "
                    "Segunda opinión en unidad de EM.",
                    False,
                ),
            ],
        },
    },
    # ------------------------------------------------------------------
    # 4. Roberto Silva — Neumología
    # ------------------------------------------------------------------
    {
        "patient": {
            "id": _uid("patient-roberto-silva"),
            "name": "Roberto Silva",
            "age": 68,
            "gender": "Masculino",
            "specialty": "Neumología",
        },
        "analysis": {
            "id": _uid("analysis-roberto-silva"),
            "domains": [
                _domain(
                    "roberto-epoc",
                    "EPOC GOLD III (Grave)",
                    "danger",
                    "EPOC estadio GOLD III: FEV1 38% del predicho, FEV1/FVC 0,54 post-broncodilatador. "
                    "Síntomas: disnea de moderados esfuerzos (mMRC 3), tos productiva matutina, "
                    "2-3 exacerbaciones/año. O2 domiciliario 2 L/min ≥ 16 h/día.",
                ),
                _domain(
                    "roberto-cor-pulmonale",
                    "Cor Pulmonale Crónico",
                    "danger",
                    "Hipertensión pulmonar secundaria a EPOC. Ecocardiograma: PAP sistólica estimada 45 mmHg, "
                    "dilatación de VD, insuficiencia tricuspídea leve. Edemas maleolares intermitentes.",
                ),
                _domain(
                    "roberto-tabaco",
                    "Tabaquismo Suspendido",
                    "ok",
                    "Ex fumador de 55 paquetes/año. Abstinencia tabáquica desde hace 3 años. "
                    "Vareniclina utilizada para cese. Sin recaídas documentadas.",
                ),
                _domain(
                    "roberto-rehab",
                    "Rehabilitación Pulmonar",
                    "warn",
                    "Programa de rehabilitación pulmonar completado con mejoría de tolerancia al esfuerzo. "
                    "Test de marcha 6 minutos: 280 m (basal 210 m). "
                    "Mantenimiento con ejercicio supervisado recomendado.",
                ),
            ],
            "alerts": [
                _alert(
                    "roberto-alert-o2",
                    "Oxigenoterapia domiciliaria crónica",
                    "danger",
                    "O2 domiciliario 2 L/min indicado por PaO2 55 mmHg en reposo (SpO2 88%). "
                    "Cumplimiento ≥ 16 h/día esencial para reducir mortalidad. "
                    "Verificar adherencia en cada consulta.",
                ),
                _alert(
                    "roberto-alert-exacerbaciones",
                    "Alto riesgo de exacerbaciones graves",
                    "danger",
                    "≥ 2 exacerbaciones/año con 1 hospitalización. Esquema GOLD D: "
                    "LAMA + LABA + ICS (tiotropio + formoterol + budesonida inhalados). "
                    "Plan de acción escrito ante primeros síntomas.",
                ),
                _alert(
                    "roberto-alert-vacunas",
                    "Vacunación — esquema vigente",
                    "ok",
                    "Vacuna antineumocócica (PCV20) y antigripal anual al día. "
                    "COVID-19: esquema completo con refuerzo bivalente.",
                ),
            ],
            "timeline": [
                _timeline(
                    "roberto-tl-dx",
                    "2010-08-20",
                    "Diagnóstico EPOC GOLD II",
                    "Espirometría post-broncodilatador: FEV1 62%, FEV1/FVC 0,58. "
                    "Tabaquismo activo 52 paquetes/año. Inicio tiotropio + SABA.",
                    False,
                ),
                _timeline(
                    "roberto-tl-cese",
                    "2022-03-01",
                    "Cese Tabáquico",
                    "Abandono del tabaco con vareniclina 1 mg/12h. Programa de cesación tabáquica completado.",
                    False,
                ),
                _timeline(
                    "roberto-tl-gold3",
                    "2022-11-15",
                    "Progresión a EPOC GOLD III",
                    "Espirometría: FEV1 38%. Intensificación a triple terapia inhalada (LAMA + LABA + ICS).",
                    True,
                ),
                _timeline(
                    "roberto-tl-o2",
                    "2023-04-10",
                    "Indicación Oxigenoterapia Crónica",
                    "Gasometría arterial: PaO2 55 mmHg, PaCO2 48 mmHg. Indicación de O2 domiciliario 2 L/min ≥ 16 h/día.",
                    True,
                ),
                _timeline(
                    "roberto-tl-rehab",
                    "2023-09-01",
                    "Programa Rehabilitación Pulmonar",
                    "Programa de 8 semanas completado. Mejoría en test de marcha: 210 → 280 m.",
                    False,
                ),
                _timeline(
                    "roberto-tl-cor",
                    "2024-06-20",
                    "Diagnóstico Cor Pulmonale",
                    "Ecocardiograma: PAP sistólica 45 mmHg, dilatación VD. "
                    "Inicio de seguimiento cardiológico conjunto.",
                    True,
                ),
            ],
        },
    },
    # ------------------------------------------------------------------
    # 5. Lucía Fernández — Ginecología/Obstetricia
    # ------------------------------------------------------------------
    {
        "patient": {
            "id": _uid("patient-lucia-fernandez"),
            "name": "Lucía Fernández",
            "age": 32,
            "gender": "Femenino",
            "specialty": "Ginecología",
        },
        "analysis": {
            "id": _uid("analysis-lucia-fernandez"),
            "domains": [
                _domain(
                    "lucia-embarazo",
                    "Embarazo de Alto Riesgo — Semana 28",
                    "warn",
                    "Gesta 2, Para 1. EG 28+3 semanas por FUR confirmada por ecografía del 1er trimestre. "
                    "Clasificado como embarazo de alto riesgo por DMG + obesidad pregestacional.",
                ),
                _domain(
                    "lucia-dmg",
                    "Diabetes Gestacional",
                    "danger",
                    "Diagnóstico de diabetes gestacional en semana 24 (PTOG: glucemia 2h 162 mg/dL). "
                    "Control glucémico con insulina NPH 10 UI/noche + plan alimentario. "
                    "Glucemias basales: 92-105 mg/dL. Glucemias postprandiales: 120-145 mg/dL.",
                ),
                _domain(
                    "lucia-fetal",
                    "Crecimiento Fetal",
                    "ok",
                    "Ecografía semana 28: peso fetal estimado en percentil 65, morfología normal, "
                    "LA normal, Doppler umbilical normal. Sin signos de macrosomía actual.",
                ),
                _domain(
                    "lucia-hta",
                    "Tensión Arterial en Embarazo",
                    "ok",
                    "PA en rango normal (115-125/70-80 mmHg) en todos los controles. "
                    "Sin proteinuria. Ausencia de criterios de preeclampsia. "
                    "Aspirina 100 mg/día como profilaxis (factores de riesgo presentes).",
                ),
            ],
            "alerts": [
                _alert(
                    "lucia-alert-macrosomia",
                    "Riesgo de Macrosomía Fetal",
                    "warn",
                    "DMG con control subóptimo en semanas 24-26 eleva riesgo de macrosomía. "
                    "Ecografía mensual de crecimiento fetal. Ajuste de insulina si glucemias postprandiales > 140 mg/dL.",
                ),
                _alert(
                    "lucia-alert-preeclampsia",
                    "Riesgo de Preeclampsia",
                    "warn",
                    "Factores de riesgo: DMG + obesidad (IMC 29,5 pregestacional). "
                    "Aspirina 100 mg/día iniciada en semana 16. Monitorización estricta de PA y proteinuria.",
                ),
                _alert(
                    "lucia-alert-insulina",
                    "Esquema insulínico activo",
                    "warn",
                    "Insulina NPH 10 UI SC nocturna. Riesgo de hipoglucemia nocturna. "
                    "Educación sobre síntomas de hipoglucemia y corrección con glucosa oral.",
                ),
            ],
            "timeline": [
                _timeline(
                    "lucia-tl-fum",
                    "2024-08-15",
                    "Última Menstruación — Inicio Embarazo",
                    "FUR 15/08/2024. Embarazo espontáneo. Inicio de ácido fólico y yodo.",
                    False,
                ),
                _timeline(
                    "lucia-tl-eco1",
                    "2024-09-20",
                    "Ecografía 1er Trimestre",
                    "EG 6+2 semanas. Vitalidad embrionaria confirmada. TN 1,4 mm. Riesgo combinado bajo.",
                    False,
                ),
                _timeline(
                    "lucia-tl-aspirin",
                    "2024-11-15",
                    "Inicio Aspirina Profiláctica",
                    "Semana 16. Inicio de AAS 100 mg/día por factores de riesgo de preeclampsia.",
                    False,
                ),
                _timeline(
                    "lucia-tl-dmg",
                    "2024-12-10",
                    "Diagnóstico Diabetes Gestacional",
                    "PTOG semana 24: glucemia basal 98 mg/dL, 2h 162 mg/dL. Diagnóstico de DMG. "
                    "Inicio plan alimentario + automonitoreo glucémico.",
                    True,
                ),
                _timeline(
                    "lucia-tl-insulina",
                    "2024-12-28",
                    "Inicio Insulinoterapia",
                    "Glucemias postprandiales persistentemente > 140 mg/dL a pesar de dieta. "
                    "Inicio insulina NPH 10 UI SC nocturna.",
                    True,
                ),
                _timeline(
                    "lucia-tl-eco28",
                    "2025-03-01",
                    "Ecografía Semana 28 — Control",
                    "PFE percentil 65, morfología normal, Doppler normal. Control en semana 32.",
                    False,
                ),
            ],
        },
    },
    # ------------------------------------------------------------------
    # 6. Jorge Mendoza — Nefrología
    # ------------------------------------------------------------------
    {
        "patient": {
            "id": _uid("patient-jorge-mendoza"),
            "name": "Jorge Mendoza",
            "age": 72,
            "gender": "Masculino",
            "specialty": "Nefrología",
        },
        "analysis": {
            "id": _uid("analysis-jorge-mendoza"),
            "domains": [
                _domain(
                    "jorge-erc",
                    "ERC Estadio 4 (Grave)",
                    "danger",
                    "Enfermedad renal crónica estadio G4A3: TFGe 22 mL/min/1,73m², proteinuria 1,8 g/24h. "
                    "Etiología: nefropatía diabética + HTA de larga evolución. "
                    "Preparación para terapia de reemplazo renal (TRR). Acceso vascular en evaluación.",
                ),
                _domain(
                    "jorge-anemia",
                    "Anemia Renal (AER)",
                    "danger",
                    "Hb 9,2 g/dL. Anemia normocítica normocrómica por deficiencia de eritropoyetina. "
                    "EPO darbepoetina alfa 40 mcg/semana SC. Ferritina 280 ng/mL, saturación Tf 24%. "
                    "Hierro IV mensual para mantener depósitos.",
                ),
                _domain(
                    "jorge-metabolismo",
                    "Alteraciones Metabólicas de ERC",
                    "warn",
                    "Hiperfosfatemia: fósforo 5,8 mg/dL (objetivo < 5,5). Carbonato de calcio 1 g/8h. "
                    "Hiperparatiroidismo secundario: PTH 380 pg/mL. Calcitriol 0,25 mcg/día. "
                    "Acidosis metabólica compensada: bicarbonato 18 mEq/L. Bicarbonato sódico 1 g/12h.",
                ),
                _domain(
                    "jorge-trr",
                    "Preparación para TRR",
                    "warn",
                    "Educación en modalidades de TRR completada: hemodiálisis vs diálisis peritoneal vs trasplante. "
                    "Acceso vascular (FAV radiocefálica izquierda) en evaluación quirúrgica. "
                    "Lista de espera trasplante renal en evaluación.",
                ),
            ],
            "alerts": [
                _alert(
                    "jorge-alert-trr",
                    "Inicio inminente de TRR",
                    "danger",
                    "TFGe 22 mL/min con tendencia descendente (-4 mL/min en 6 meses). "
                    "Síntomas urémicos incipientes: astenia marcada, náuseas matutinas. "
                    "TRR estimada en 3-6 meses según evolución.",
                ),
                _alert(
                    "jorge-alert-farmacologia",
                    "Ajuste farmacológico por ERC avanzada",
                    "danger",
                    "Múltiples fármacos con necesidad de ajuste por TFGe < 30 mL/min: "
                    "metformina CONTRAINDICADA (suspendida), AINEs contraindicados, "
                    "ajuste de dosis de antibióticos. Revisar toda prescripción nueva.",
                ),
                _alert(
                    "jorge-alert-hiperpotasemia",
                    "Riesgo de Hiperpotasemia",
                    "warn",
                    "Potasio 5,2 mEq/L. Dieta hipopotasémica. Riesgo aumentado si inicia IECA/ARA-II. "
                    "Monitorización quincenal de electrolitos.",
                ),
                _alert(
                    "jorge-alert-acceso",
                    "Acceso vascular para hemodiálisis — en proceso",
                    "warn",
                    "FAV radiocefálica izquierda pendiente de evaluación quirúrgica. "
                    "Preservar vena cefálica izquierda: NO venopunciones en ese brazo.",
                ),
            ],
            "timeline": [
                _timeline(
                    "jorge-tl-dm2",
                    "2005-01-01",
                    "Diagnóstico DM2 e HTA",
                    "Diagnóstico simultáneo de DM2 e HTA a los 51 años. Inicio metformina + enalapril.",
                    False,
                ),
                _timeline(
                    "jorge-tl-nefropatia",
                    "2015-06-10",
                    "Diagnóstico Nefropatía Diabética",
                    "Biopsia renal: glomeruloesclerosis nodular (Kimmelstiel-Wilson). "
                    "TFGe 58 mL/min. Proteinuria 1,2 g/24h. ERC estadio G2.",
                    True,
                ),
                _timeline(
                    "jorge-tl-erc3",
                    "2020-03-15",
                    "Progresión ERC Estadio 3",
                    "TFGe 42 mL/min. Suspensión de metformina. Inicio darbepoetina alfa por Hb 10,8 g/dL.",
                    True,
                ),
                _timeline(
                    "jorge-tl-erc4",
                    "2023-09-01",
                    "Progresión ERC Estadio 4",
                    "TFGe 26 mL/min. Inicio programa de preparación para TRR. "
                    "Educación en modalidades dialíticas y trasplante.",
                    True,
                ),
                _timeline(
                    "jorge-tl-fav",
                    "2025-01-15",
                    "Evaluación para FAV Radiocefálica",
                    "Ecodoppler venoso: vena cefálica izquierda calibre 3,2 mm. "
                    "Candidato a FAV. Cirugía vascular programada.",
                    True,
                ),
                _timeline(
                    "jorge-tl-actual",
                    "2025-03-20",
                    "Control Nefrológico — TFGe 22 mL/min",
                    "TFGe 22 mL/min. Síntomas urémicos incipientes. Hb 9,2 g/dL. "
                    "Inicio inminente de TRR en próximos 3-6 meses.",
                    True,
                ),
            ],
        },
    },
]


# ---------------------------------------------------------------------------
# Función principal de seed
# ---------------------------------------------------------------------------


def _build_sync_url() -> str:
    """Obtiene la URL sincrónica para psycopg desde DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError(
            "La variable de entorno DATABASE_URL no está configurada. "
            "Copia .env.example a .env y configura DATABASE_URL."
        )
    return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://").replace(
        "postgresql://", "postgresql+psycopg://"
    )


def seed(session: Session) -> None:
    """Inserta los pacientes y análisis si no existen aún."""
    count = session.execute(text("SELECT COUNT(*) FROM patients")).scalar()
    if count and count > 0:
        logger.info("Ya existen %d pacientes en la base de datos. Omitiendo seed.", count)
        return

    logger.info("Insertando %d pacientes de demostración...", len(PATIENTS_DATA))
    now = datetime.now(UTC)

    for entry in PATIENTS_DATA:
        p = entry["patient"]
        a = entry["analysis"]

        # Insertar paciente
        session.execute(
            text(
                """
                INSERT INTO patients (id, name, age, gender, specialty, created_at)
                VALUES (:id, :name, :age, :gender, :specialty, :created_at)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": str(p["id"]),
                "name": p["name"],
                "age": p["age"],
                "gender": p["gender"],
                "specialty": p["specialty"],
                "created_at": now,
            },
        )

        # Construir raw_llm_response simulando lo que el LLM retornaría
        raw_response = json.dumps(
            {
                "domains": a["domains"],
                "alerts": a["alerts"],
                "timeline": a["timeline"],
            },
            ensure_ascii=False,
        )

        # Insertar análisis clínico
        session.execute(
            text(
                """
                INSERT INTO clinical_analyses (
                    id, patient_id, domains, alerts, timeline,
                    raw_llm_response, proveedor, modelo,
                    tokens_entrada, tokens_salida, tiempo_procesamiento_ms,
                    created_at
                )
                VALUES (
                    :id, :patient_id, CAST(:domains AS jsonb), CAST(:alerts AS jsonb), CAST(:timeline AS jsonb),
                    :raw_llm_response, :proveedor, :modelo,
                    :tokens_entrada, :tokens_salida, :tiempo_procesamiento_ms,
                    :created_at
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "id": str(a["id"]),
                "patient_id": str(p["id"]),
                "domains": json.dumps(a["domains"], ensure_ascii=False),
                "alerts": json.dumps(a["alerts"], ensure_ascii=False),
                "timeline": json.dumps(a["timeline"], ensure_ascii=False),
                "raw_llm_response": raw_response,
                "proveedor": "seed",
                "modelo": "seed-data-v1",
                "tokens_entrada": None,
                "tokens_salida": None,
                "tiempo_procesamiento_ms": 0,
                "created_at": now,
            },
        )
        logger.info("  ✓ Paciente: %s (%s)", p["name"], p["specialty"])

    session.commit()
    logger.info("Seed completado exitosamente.")


def _create_tables(engine: object) -> None:
    """Crea todas las tablas usando Base.metadata.create_all (sync)."""
    import app.db.models.clinical_analysis  # noqa: F401
    import app.db.models.patient  # noqa: F401
    from app.db.base import Base

    Base.metadata.create_all(engine)  # type: ignore[arg-type]
    logger.info("Tablas creadas (create_all).")


def main() -> None:
    """Punto de entrada principal."""
    try:
        sync_url = _build_sync_url()
    except RuntimeError as e:
        logger.error("%s", e)
        sys.exit(1)

    try:
        engine = create_engine(
            sync_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 5},
        )
        _create_tables(engine)
        with Session(engine) as session:
            seed(session)
    except Exception as e:
        logger.error("Error al conectar con la base de datos: %s", e)
        logger.error(
            "Asegurate de que la base de datos esté corriendo y DATABASE_URL sea correcta."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
