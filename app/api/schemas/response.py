from pydantic import BaseModel


class ResumenEjecutivoTecnico(BaseModel):
    trayectoria_clinica: str
    intervenciones_consolidadas: str
    estado_seguridad: str
    impresion_diagnostica: str


class AnalyzeResponse(BaseModel):
    resumen_ejecutivo: ResumenEjecutivoTecnico | None = None
    resumen_texto: str
    proveedor: str
    modelo: str
    tokens_entrada: int | None = None
    tokens_salida: int | None = None
    tiempo_procesamiento_ms: int
