from pydantic import BaseModel


class ResumenEjecutivoTecnico(BaseModel):
    trayectoria_clinica: str
    intervenciones_consolidadas: str
    estado_seguridad: str


class AnalyzeResponse(BaseModel):
    resumen_ejecutivo: ResumenEjecutivoTecnico | None = None
    proveedor: str
    modelo: str
    tokens_entrada: int | None = None
    tokens_salida: int | None = None
    tiempo_procesamiento_ms: int
