# Guia Docker Compose

Esta guia cubre como levantar, operar y depurar el servicio `api` usando Docker Compose. El archivo de configuracion es `docker-compose.yml` en la raiz del proyecto.

---

## Requisitos previos

- **Docker Desktop** instalado y corriendo (version 24 o superior recomendada)
- Archivo `.env` configurado en la raiz del proyecto (ver seccion siguiente)

---

## Configuracion inicial

El proyecto usa un archivo `.env` para inyectar variables de entorno al contenedor. Este archivo **no se commitea** (esta en `.gitignore`). El template esta en `.env.example`.

Crear el archivo `.env` en la raiz del proyecto:

```bash
cp .env.example .env
```

Luego editar `.env` con los valores reales:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-tu-clave-aqui
MODEL_NAME=gpt-4o
LLM_PROVIDER=openai

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

| Variable         | Descripcion                                              | Valores posibles           |
|------------------|----------------------------------------------------------|----------------------------|
| `OPENAI_API_KEY` | Clave de API de OpenAI. Requerida para el proveedor LLM  | `sk-...`                   |
| `MODEL_NAME`     | Modelo a usar para la inferencia                         | `gpt-4o`, `gpt-4o-mini`    |
| `LLM_PROVIDER`   | Proveedor del LLM                                        | `openai`                   |
| `APP_ENV`        | Entorno de ejecucion                                     | `development`, `production` |
| `LOG_LEVEL`      | Nivel de detalle de los logs                             | `DEBUG`, `INFO`, `WARNING`  |

> El archivo `.env.example` si se commitea y sirve como referencia para otros desarrolladores. Nunca commitear `.env` con claves reales.

---

## Comandos principales

### Levantar el servicio en background

```bash
docker compose up -d
```

### Ver logs en tiempo real

```bash
docker compose logs -f api
```

### Detener el servicio

```bash
docker compose down
```

### Reconstruir la imagen despues de cambios en el codigo

Necesario cada vez que se modifica `Dockerfile`, `pyproject.toml` o cualquier archivo de la aplicacion:

```bash
docker compose up -d --build
```

### Ver el estado del servicio y del healthcheck

```bash
docker compose ps
```

La columna `STATUS` muestra `healthy` cuando el contenedor paso el healthcheck de `GET /health`.

---

## Verificar que el servicio funciona

### 1. Health check

```bash
curl http://localhost:8000/health
```

Respuesta esperada:

```json
{
  "status": "healthy",
  "service": "clinic-copilot-nlp",
  "version": "0.1.0"
}
```

### 2. Analizar una historia clinica

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "historia_clinica": "Varon de 65 anos con HTA y DM2 de larga evolucion. Acude por dolor toracico opresivo de 2 horas de evolucion. ECG: elevacion del ST en V1-V4. Troponina positiva. Diagnostico: SCACEST anterior. Tratamiento: fibrinolisis con alteplasa. Evolucion favorable, alta a los 5 dias."
  }'
```

Respuesta esperada (estructura del JSON):

```json
{
  "trayectoria_clinica": "...",
  "intervenciones_consolidadas": "...",
  "estado_de_seguridad": "...",
  "sintesis_tecnica": "..."
}
```

> Si el texto es demasiado corto o carece de informacion clinica relevante, el LLM igualmente devuelve la estructura pero con menor detalle en cada seccion.

---

## Estructura del servicio

El archivo `docker-compose.yml` define un unico servicio:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

| Directiva              | Efecto                                                                        |
|------------------------|-------------------------------------------------------------------------------|
| `build: .`             | Construye la imagen desde el `Dockerfile` en la raiz del proyecto             |
| `ports: "8000:8000"`   | Expone el puerto 8000 del contenedor en el puerto 8000 del host               |
| `env_file: .env`       | Inyecta todas las variables del archivo `.env` al contenedor                  |
| `restart: unless-stopped` | Reinicia automaticamente el contenedor si falla, a menos que se detenga manualmente |
| `healthcheck`          | Verifica cada 30s que `GET /health` responde con HTTP 200                     |
| `start_period: 10s`    | Da 10 segundos de gracia antes de empezar a contar fallos del healthcheck     |

---

## Troubleshooting

### El contenedor no inicia

Verificar que el archivo `.env` existe y que `OPENAI_API_KEY` tiene un valor valido:

```bash
docker compose logs api --tail=50
```

Los errores de configuracion aparecen en las primeras lineas del log al arrancar la aplicacion.

### Puerto 8000 ya esta en uso

Cambiar el mapeo de puertos en `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"   # usar 8001 en el host, 8000 sigue siendo el puerto interno
```

Luego reconstruir:

```bash
docker compose up -d --build
```

Las llamadas al API deben hacerse contra `http://localhost:8001`.

### Error 503 en `POST /api/analyze`

El servicio esta corriendo pero no puede comunicarse con OpenAI. Causas posibles:

- La `OPENAI_API_KEY` es invalida o expiro
- La cuenta de OpenAI no tiene credito disponible
- Problemas de conectividad de red desde el contenedor

Verificar logs:

```bash
docker compose logs api --tail=50
```

### Error 422 en `POST /api/analyze`

El body del request esta mal formado. Causas posibles:

- El campo `historia_clinica` no existe en el JSON
- El campo `historia_clinica` esta vacio o es `null`
- El `Content-Type` del request no es `application/json`

Revisar el ejemplo de la seccion de verificacion mas arriba y asegurarse de que el JSON es valido.

### Ver logs detallados

```bash
docker compose logs api --tail=50
```

Para logs en tiempo real:

```bash
docker compose logs -f api
```

### Reconstruir desde cero

Si hay problemas persistentes que no se resuelven con `--build`, hacer un ciclo completo:

```bash
docker compose down && docker compose up -d --build
```

Esto detiene el contenedor, destruye la red de Docker Compose y reconstruye la imagen desde el principio.

---

## Desarrollo local (sin Docker)

Si se prefiere correr la aplicacion directamente en el host para desarrollo, sin pasar por Docker:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

El flag `--reload` activa el hot-reload de Uvicorn: cualquier cambio en el codigo reinicia automaticamente el servidor.

El archivo `.env` debe estar en la raiz del proyecto tambien en este modo, ya que la aplicacion lo lee al arrancar.

> Requiere Python 3.14 y `uv` instalado. Ver `pyproject.toml` para las dependencias del proyecto.

---

## Pruebas con los casos de prueba incluidos

El proyecto incluye 5 casos de prueba estandarizados en el directorio `data/test_cases/`. Cada archivo contiene una historia clinica real de una especialidad distinta, en el formato exacto que el endpoint `POST /api/analyze` espera.

### Ejecutar un caso de prueba contra el API

Con el servicio corriendo (ya sea via Docker o en modo local), ejecutar desde la raiz del proyecto:

```bash
# Leer la historia clínica del caso y enviarla al API
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"historia_clinica\": $(cat data/test_cases/tc_001.json | python3 -c \"import sys,json; print(json.dumps(json.load(sys.stdin)['historia_clinica']))\")}"
```

Reemplazar `tc_001.json` por el archivo que corresponda al caso que se quiere probar.

### Casos disponibles

| Archivo       | Especialidad    | Que valida                                                                      |
|---------------|-----------------|---------------------------------------------------------------------------------|
| `tc_001.json` | Cardiologia     | Descompensacion de ICC con multiples comorbilidades (HTA, FA, FEVI reducida)    |
| `tc_002.json` | Endocrinologia  | DM2 con complicaciones cronicas (neuropatia, retinopatia) y ajuste terapeutico  |
| `tc_003.json` | Neurologia      | Seguimiento post-ACV con reperfusion, secuelas funcionales y anticoagulacion    |
| `tc_004.json` | Nefrologia      | ERC avanzada con manejo de anemia, HPT secundario y preparacion para dialisis   |
| `tc_005.json` | Neumologia      | EPOC severo con cor pulmonale, oxigenoterapia cronica y exacerbaciones recientes |

### Nota importante al usar Docker

El directorio `data/` **no se copia dentro del contenedor** (esta listado en `.dockerignore`). Los comandos `curl` con `cat data/test_cases/...` deben ejecutarse desde la maquina host, no desde dentro del contenedor. El endpoint queda expuesto en `http://localhost:8000`, por lo que los comandos funcionan correctamente desde el host apuntando a ese puerto.
