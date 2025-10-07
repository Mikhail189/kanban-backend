from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.file import File as FileModel
from app.core.database import async_session
from app.core.s3_client import s3_client
from sqlalchemy import select
from datetime import datetime

import os
router = APIRouter()

BUCKET = os.getenv("YANDEX_S3_BUCKET")

@router.post("/{task_id}")
async def upload_file(task_id: str, file: UploadFile = File(...)):
    file_data = await file.read()
    s3_key = f"{task_id}/{file.filename}"

    async with async_session() as session:
        #Проверяем, есть ли уже файл для этой задачи
        result = await session.execute(select(FileModel).where(FileModel.task_id == task_id))
        existing_file = result.scalar_one_or_none()

        #Если файл уже есть — удаляем старый из S3
        if existing_file:
            old_key = f"{task_id}/{existing_file.filename}"
            try:
                s3_client.delete_object(Bucket=BUCKET, Key=old_key)
            except Exception as e:
                print(f"Ошибка при удалении старого файла из S3: {e}")

            #Загружаем новый файл
            s3_client.put_object(
                Bucket=BUCKET,
                Key=s3_key,
                Body=file_data,
                ContentType=file.content_type,
            )

            #Обновляем данные в БД
            existing_file.filename = file.filename
            existing_file.url = f"https://{BUCKET}.storage.yandexcloud.net/{s3_key}"
            existing_file.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(existing_file)

            return {
                "status": "updated",
                "filename": existing_file.filename,
                "url": existing_file.url
            }

        #Если файла нет — создаем новый
        else:
            s3_client.put_object(
                Bucket=BUCKET,
                Key=s3_key,
                Body=file_data,
                ContentType=file.content_type,
            )

            url = f"https://{BUCKET}.storage.yandexcloud.net/{s3_key}"
            new_file = FileModel(task_id=task_id, filename=file.filename, url=url)
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)

            return {
                "status": "created",
                "filename": new_file.filename,
                "url": new_file.url
            }



@router.get("/{task_id}")
async def get_file(task_id: str):
    async with async_session() as session:
        result = await session.execute(select(FileModel).where(FileModel.task_id == task_id))
        file = result.scalar_one_or_none()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file


@router.delete("/{task_id}")
async def delete_file(task_id: str):
    async with async_session() as session:
        result = await session.execute(select(FileModel).where(FileModel.task_id == task_id))
        file = result.scalar_one_or_none()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        #Удаляем из S3
        try:
            s3_client.delete_object(Bucket=BUCKET, Key=f"{task_id}/{file.filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 deletion failed: {e}")

        #Удаляем из базы
        await session.delete(file)
        await session.commit()

    return {"detail": "File deleted"}
