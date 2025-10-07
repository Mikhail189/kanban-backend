from fastapi import APIRouter, Depends, HTTPException
from fastapi import UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskUpdateStatus
from app.api.routes.websocket import broadcast
import httpx

FILE_SERVICE_URL = "http://file-service:8001/files"

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskRead)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):

    new_task = Task(**task.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Отправляем событие всем клиентам
    await broadcast({
        "event": "task_created",
        "task": TaskRead.from_orm(new_task).model_dump()
    })

    return new_task


@router.get("/", response_model=list[TaskRead])
async def get_tasks(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Task))
    tasks = result.scalars().all()

    async with httpx.AsyncClient() as client:
        for task in tasks:
            # Получаем файл для каждой задачи
            response = await client.get(f"http://file-service:8001/files/{task.id}")
            if response.status_code == 200:
                task.file = response.json()
            else:
                task.file = None

    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли задача
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Преобразуем задачу в словарь
    task_data = TaskRead.from_orm(task).model_dump()

    # Пытаемся получить файл из file-service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://file-service:8001/files/{task_id}")
            if response.status_code == 200:
                task_data["file"] = response.json()
            else:
                task_data["file"] = None
        except Exception:
            task_data["file"] = None  # если file-service недоступен

    return task_data


@router.patch("/{task_id}/status", response_model=TaskRead)
async def update_task_status(task_id: int, data: TaskUpdateStatus, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = data.status
    await db.commit()
    await db.refresh(task)

    await broadcast({
        "event": "task_updated",
        "task": TaskRead.from_orm(task).model_dump()
    })

    return task


@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Сохраняем данные, прежде чем удалить (иначе объект станет "detached")
    deleted_task = TaskRead.from_orm(task)

    await db.delete(task)
    await db.commit()

    await broadcast({
        "event": "task_deleted",
        "task": deleted_task.model_dump()
    })

    return deleted_task


@router.post("/{task_id}/files")
async def attach_file_to_task(
    task_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, существует ли задача
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Отправляем файл в file-service
    async with httpx.AsyncClient() as client:
        files = {'file': (file.filename, await file.read())}
        response = await client.post(f"http://file-service:8001/files/{task_id}", files=files)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="File upload failed")

    return {
        "task_id": task_id,
        "file_info": response.json()
    }


@router.delete("/{task_id}/files")
async def delete_file_from_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Проверяем, существует ли задача
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Отправляем запрос в file-service для удаления файла
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://file-service:8001/files/{task_id}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="File deletion failed")

    return {
        "task_id": task_id,
        "detail": "File deleted successfully"
    }
