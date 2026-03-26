# This file is kept for backwards compatibility.
# The actual application entry point is app/main.py
# Run with: uv run uvicorn app.main:app --reload
raise RuntimeError(
    "Run the app with: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
)
