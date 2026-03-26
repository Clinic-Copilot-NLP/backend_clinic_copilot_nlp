# AGENTS.md — backend_clinic_copilot_nlp

## Project Overview

FastAPI backend for the Clinical Copilot NLP project. Receives patient clinical histories
in free-text Spanish and returns a structured Executive Technical Summary using an LLM.
The LLM backend is swappable via the Strategy pattern (OpenAI, Ollama, HuggingFace).
The project is in Phase 1 — infrastructure and baseline pipeline. Only OpenAI is fully
implemented; Ollama and HuggingFace providers exist as stubs.

---

## Commands

All commands use `uv run`. Never use pip, poetry, or any other package manager.

```bash
# Install / sync dependencies
uv sync

# Run development server (hot reload)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run production server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker (build and run)
docker compose up --build
docker compose up -d          # detached
docker compose down

# Run tests (pytest + httpx must be added to dev deps first)
uv run pytest
uv run pytest tests/test_analyze.py                     # single file
uv run pytest tests/test_analyze.py::test_analyze_ok    # single test
uv run pytest -x -v                                     # fail fast, verbose

# Lint (ruff check)
uv run ruff check .
uv run ruff check . --fix

# Format (ruff format)
uv run ruff format .
uv run ruff format . --check   # CI dry-run

# Type check
uv run mypy app/
```

> No ruff, mypy, or pytest config exists in pyproject.toml yet. See recommended config below.

---

## Architecture

```
app/
  main.py                        # FastAPI app, lifespan, global error handlers
  core/
    config.py                    # pydantic-settings Settings class, get_settings()
    prompts/
      clinical.py                # SYSTEM_PROMPT constant + build_user_prompt()
    services/
      summarizer.py              # ClinicalSummarizerService — orchestrates prompt + LLM call
  api/
    routes/
      health.py                  # GET /health
      analyze.py                 # POST /api/analyze
    schemas/
      request.py                 # AnalyzeRequest (Pydantic input model)
      response.py                # AnalyzeResponse, ResumenEjecutivoTecnico (output models)
  infrastructure/
    llm/
      base.py                    # LLMProvider ABC, LLMResponse, LLMProviderError
      factory.py                 # get_llm_provider(settings) — selects provider at startup
      openai_provider.py         # OpenAIProvider (fully implemented)
      ollama.py                  # OllamaProvider (stub — raises NotImplementedError)
      huggingface.py             # HuggingFaceProvider (stub — raises NotImplementedError)
```

**Strategy pattern for LLM providers:**
- `LLMProvider` in `base.py` is the abstract interface. Every provider implements
  `generate(system_prompt, user_prompt) -> LLMResponse` and the `provider_name` property.
- `factory.py` instantiates the concrete provider at startup based on `LLM_PROVIDER` env var.
- `app.state.llm_provider` holds the live instance; routes access it via `request.app.state`.
- Service layer (`summarizer.py`) depends on the `LLMProvider` interface, never on a
  concrete class.

**Where to add new things:**
- New LLM provider: `app/infrastructure/llm/<name>.py` + register in `factory.py`
- New API endpoint: `app/api/routes/<name>.py` + `app.include_router(...)` in `main.py`
- New schemas: `app/api/schemas/`
- New service: `app/core/services/`
- New prompt: `app/core/prompts/`

---

## Code Style

No ruff or mypy config exists yet. Add this to `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]   # handled by formatter

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.mypy]
python_version = "3.13"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Import order (isort / ruff I rules):**
1. Standard library (`json`, `logging`, `time`, `abc`, etc.)
2. Third-party (`fastapi`, `openai`, `pydantic`, etc.)
3. First-party (`app.*`)

**Type annotations:**
- Use `X | Y` union syntax (Python 3.10+), never `Optional[X]` or `Union[X, Y]`.
- Annotate all function signatures — parameters and return types.
- Use `str | None` not `Optional[str]`.

**Naming conventions:**
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`
- Settings fields: `UPPER_SNAKE_CASE` (pydantic-settings convention)

**Other conventions observed:**
- `logging.getLogger(__name__)` at module level — one logger per file.
- No inline lambdas for validators; use `@field_validator` with `@classmethod`.
- `@lru_cache` on `get_settings()` — settings are a singleton.

---

## Pydantic & FastAPI Patterns

**Pydantic models:**
- All models inherit from `pydantic.BaseModel` directly (no custom base class).
- Use `Field(...)` with `min_length`, `max_length`, and `description` for input validation.
- Validators use `@field_validator("field_name", mode="before")` with `@classmethod`.
- Union fields use `X | None = None` syntax, never `Optional`.
- `SecretStr` for secrets — always call `.get_secret_value()` when passing to clients.

**pydantic-settings:**
- `Settings` inherits from `BaseSettings` with `SettingsConfigDict(env_file=".env")`.
- `get_settings()` is decorated with `@lru_cache` and returns a singleton.
- Never instantiate `Settings()` directly in routes or services — always call `get_settings()`.

**FastAPI patterns:**
- Routers: `router = APIRouter()` in each route module; registered in `main.py`.
- Prefix and tags are set on `include_router`, not on the `APIRouter()` constructor.
- LLM provider is accessed via `request.app.state.llm_provider` — no `Depends` for state.
- `lifespan` context manager (not deprecated `on_event`) for startup/shutdown logic.
- Services are instantiated directly inside route handlers (`ClinicalSummarizerService()`),
  not injected via `Depends`. Keep services stateless.
- All route handlers are `async def`.

---

## Error Handling

**Domain exception:**
- `LLMProviderError(message, provider, original_error)` defined in `base.py`.
- Raised by every provider when the LLM call fails — wraps the original SDK error with
  `raise LLMProviderError(...) from e`.
- Registered as a global exception handler in `main.py` returning HTTP 503.
- Also caught locally in route handlers and re-raised as `HTTPException(503)` for safety.

**Mapping:**
- `LLMProviderError` -> HTTP 503 (service unavailable)
- `NotImplementedError` (stub providers) -> HTTP 501 (not implemented)
- Pydantic validation errors are handled automatically by FastAPI (HTTP 422).

**Rules:**
- Never leak internal exception messages or stack traces to the HTTP response body.
- Use `logger.error(...)` before raising or returning error responses.
- Graceful degradation in `_parse_llm_response`: if JSON parsing fails, return raw text
  rather than raising — log a warning and set `resumen_ejecutivo=None`.

---

## Language Rules

**Variable names, function names, class names:** English only.

**Domain field names in schemas:** Spanish, matching the clinical domain exactly.
Examples: `historia_clinica`, `trayectoria_clinica`, `resumen_ejecutivo`,
`tokens_entrada`, `tiempo_procesamiento_ms`.

**Docstrings and inline comments:** Spanish. This project targets Spanish-speaking
medical professionals and the codebase reflects that context.

**Log messages:** Mixed — infrastructure logs in English (`"Calling OpenAI model=..."`),
domain/service logs in Spanish (`"Iniciando análisis clínico"`, `"Análisis completado"`).
New code should follow the same pattern: infrastructure = English, domain = Spanish.

**Prompts:** Always in Spanish. The LLM must respond in Spanish medical language.

---

## LLM Provider Strategy

To add a new provider (example: Anthropic Claude):

1. **Create the provider file** at `app/infrastructure/llm/anthropic_provider.py`:
   ```python
   import logging
   from anthropic import AsyncAnthropic, APIError
   from app.infrastructure.llm.base import LLMProvider, LLMResponse, LLMProviderError
   from app.core.config import Settings

   logger = logging.getLogger(__name__)

   class AnthropicProvider(LLMProvider):
       def __init__(self, settings: Settings) -> None:
           self._model = settings.MODEL_NAME
           self._client = AsyncAnthropic(
               api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
           )

       @property
       def provider_name(self) -> str:
           return "anthropic"

       async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
           try:
               # ... call client, return LLMResponse(...)
               pass
           except APIError as e:
               raise LLMProviderError(str(e), self.provider_name, e) from e
   ```

2. **Add the required setting** to `app/core/config.py`:
   ```python
   ANTHROPIC_API_KEY: SecretStr = SecretStr("")
   ```

3. **Register in factory** at `app/infrastructure/llm/factory.py`:
   ```python
   elif provider_name == "anthropic":
       from app.infrastructure.llm.anthropic_provider import AnthropicProvider
       return AnthropicProvider(settings)
   ```

4. **Update `.env.example`** with the new key.

5. **Rules for provider implementations:**
   - Always catch specific SDK exceptions and wrap them in `LLMProviderError`.
   - Always catch a broad `Exception` as the final fallback.
   - Always use `raise ... from e` to preserve the exception chain.
   - Return a fully populated `LLMResponse` — never return `None`.
   - `tokens_input` and `tokens_output` may be `None` if the API does not report usage.

---

## Environment & Configuration

Copy `.env.example` to `.env` and fill in the values. Never commit `.env`.

```bash
# LLM Provider — selects which backend is loaded at startup
LLM_PROVIDER=openai          # options: openai | ollama | huggingface

# OpenAI settings (used when LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o

# Application
APP_ENV=development          # development | production
LOG_LEVEL=INFO
```

**Rules:**
- All secrets must be typed as `SecretStr` in `Settings`. Never use `str` for API keys.
- Access secret values only via `.get_secret_value()` — never log or expose them.
- `get_settings()` is cached with `@lru_cache`. In tests, invalidate the cache with
  `get_settings.cache_clear()` before patching environment variables.
- `MAX_HISTORIA_CHARS = 50_000` is enforced both in `Settings` (config) and in
  `AnalyzeRequest.historia_clinica` (Pydantic `max_length`). Keep these in sync.
- Do not hardcode model names, API keys, or endpoints anywhere in the code.
