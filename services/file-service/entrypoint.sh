#!/bin/bash
set -e

echo "⏳ Waiting for PostgreSQL to start..."
# ждем, пока база поднимется (обычно 5–10 секунд)
until nc -z file-db 5432; do
  sleep 1
done

echo "✅ Database is up! Running migrations..."
alembic upgrade head

echo "🚀 Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001
