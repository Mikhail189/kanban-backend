# 🗂️ Kanban Backend (FastAPI + PostgreSQL + Docker)

Микросервисный backend для **Kanban-системы** с возможностью прикрепления файлов и оповещениями через **WebSocket**.  
Проект полностью контейнеризован с помощью **Docker Compose** и включает два сервиса.

---

## 🧩 Архитектура

### 1️⃣ board-service
Основной сервис (**FastAPI**) для управления задачами:
- Создание, обновление и удаление задач  
- Изменение статуса  
- Интеграция с **file-service**  
- Поддержка **WebSocket** для уведомлений:
  - `task_created`
  - `task_updated`
  - `task_deleted`

### 2️⃣ file-service
Отдельный сервис для загрузки, хранения и удаления файлов в **Yandex Object Storage (S3)**.  
Файлы привязываются к задачам по `task_id`.

---

## ⚙️ Технологии

- 🐍 **Python 3.11**  
- ⚡ **FastAPI**  
- 🗄️ **SQLAlchemy + Alembic**  
- 🐘 **PostgreSQL**  
- 🌐 **HTTPX** — взаимодействие между сервисами  
- 🧪 **Pytest + pytest-asyncio**  
- 🐳 **Docker Compose**

---

## 🚀 Запуск проекта

Перед запуском убедись, что установлен **Docker**.

Запуск выполняется одной командой:

```bash
docker compose up --build
```
## 🚀 После сборки сервисы будут доступны по адресам

| Сервис        | URL                          | Назначение              |
|----------------|------------------------------|--------------------------|
| board-service  | [http://localhost:8000/docs](http://localhost:8000/docs) | API задач (Swagger UI)  |
| file-service   | [http://localhost:8001/docs](http://localhost:8001/docs) | API файлов              |

---

## 💬 WebSocket

Для получения уведомлений о событиях подключайся к адресу:

```bash
ws://localhost:8000/ws
```

## 💬 Пример события

```json
{
  "event": "task_created",
  "task": {
    "id": 1,
    "title": "New task",
    "status": "todo"
  }
}
```
## 🧪 Тестирование

Проект использует отдельные тестовые базы данных, чтобы не затрагивать production-данные.  
При запуске тестов автоматически создаются и мигрируются базы:

- `kanban-db-test`
- `file-db-test`

Запуск тестов:

```bash
docker compose exec board-service pytest -v
```

## 🧰 Переменные окружения

Каждый сервис использует свой `.env` файл.

Пример для `file-service/.env`:

```env
YANDEX_S3_BUCKET=<BUCKET>
YANDEX_S3_ENDPOINT=https://storage.yandexcloud.net
YANDEX_S3_ACCESS_KEY_ID=<YOUR_ACCESS_KEY>
YANDEX_S3_SECRET_ACCESS_KEY=<YOUR_SECRET_KEY>
⚠️ Важно:
Ключи доступа к Yandex S3 не хранятся в репозитории.
Используй .env.example, добавив свои ключи.
```
## 🧠 Примечания

- Все миграции выполняются автоматически при старте контейнера.  
- При тестировании используются тестовые базы, изолированные от production.  
- **WebSocket-уведомления** доступны сразу после запуска без дополнительной настройки.