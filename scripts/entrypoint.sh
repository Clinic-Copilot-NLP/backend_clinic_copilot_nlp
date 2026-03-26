#!/bin/bash
set -e

echo "Seeding database (creates tables + dummy data)..."
python scripts/seed.py

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
