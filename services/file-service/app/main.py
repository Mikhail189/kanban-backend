from fastapi import FastAPI
from app.api.routes import files

app = FastAPI(
    title="File Service",
    description="Микросервис для загрузки и скачивания файлов через Yandex S3",
    version="1.0.0",
)

# Регистрируем роуты
app.include_router(files.router, prefix="/files", tags=["files"])


@app.get("/")
async def root():
    return {"message": "File service is running 🚀"}
