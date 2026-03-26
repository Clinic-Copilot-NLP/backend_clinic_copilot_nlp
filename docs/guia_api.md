# Guía Backend API

## Base URL

http://localhost:8000/api/v1

## Pacientes

### Get

```
GET /api/v1/patients
```

Response:

```json
[
  id: {
    name,
    age,
    gender ("M"|"F"),
    specialty
  }
]
```

### Post

```
POST /api/v1/patients
Body: { name: string, age: integer, gender: string "F"|"M", specialty: string }
```

Response:
```
{
  id: string
}
```

## Resumen clínico por paciente

### Post 

> Llamado al LLM para analizar.

```
POST /api/v1/patients/{id}/analyze
Body: { historia_clinica: string }
```

Response:
```
status code: 204 | 422 | 500,

responses={
    204: {"description": "Análisis guardado correctamente"},
    422: {"description": "Historia clínica inválida"},
    500: {"description": "Error interno del servidor"},
}
```

### Get

```
GET /api/v1/patients/{id}/summary
```

Response:

```json
{
  patient_id: string,
  domains: [{ id, title, status: "ok"|"warn"|"danger", description }],
  alerts: [{ id, title, status: "ok"|"warn"|"danger", description }],
  timeline: [{ id, date, title, description, is_critical: bool }],
}
```
