#!/bin/sh
set -e

echo "🚀 Starting entrypoint..."

# --- Основная база ---
echo "⏳ Waiting for main PostgreSQL (kanban-db) to start..."
while ! nc -z kanban-db 5432; do
  sleep 2
done
echo "✅ Main database is up!"

echo "🏗️ Applying migrations to main database..."
alembic upgrade head
echo "✅ Main database migrated successfully!"

# --- Тестовая база ---
if [ -n "$TEST_DATABASE_URL" ]; then
  echo "⏳ Waiting for test PostgreSQL (kanban-db-test) to start..."
  while ! nc -z kanban-db-test 5432; do
    sleep 2
  done
  echo "✅ Test database is up!"

  echo "🏗️ Applying migrations to test database..."
  DATABASE_URL=$TEST_DATABASE_URL alembic upgrade head
  echo "✅ Test database migrated successfully!"
else
  echo "⚠️ TEST_DATABASE_URL not set — skipping test DB migrations."
fi

# --- Запуск приложения ---
echo "🚀 Starting FastAPI app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000



