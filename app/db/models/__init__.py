# Importar todos los modelos para que Alembic los detecte en la metadata
from app.db.models.clinical_analysis import ClinicalAnalysis
from app.db.models.patient import Patient

__all__ = ["Patient", "ClinicalAnalysis"]
