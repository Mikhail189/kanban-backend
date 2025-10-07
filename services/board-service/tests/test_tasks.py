import pytest
import io
import httpx

@pytest.mark.asyncio
async def test_create_task(client):
    response = await client.post("/tasks/", json={
        "title": "Test task",
        "description": "Check CRUD logic",
        "status": "To Do"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test task"
    assert data["status"] == "To Do"



@pytest.mark.asyncio
async def test_get_task(client):
    create_resp = await client.post("/tasks/",json={
        "title": "Test GET",
        "description": "Check GET endpoint"}
    )
    assert create_resp.status_code == 200

    created_task = create_resp.json()
    task_id = created_task["id"]

    # Получаем задачу
    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    task_data = get_resp.json()

    assert task_data["title"] == "Test GET"
    assert task_data["description"] == "Check GET endpoint"
    assert task_data["status"] == "To Do"


@pytest.mark.asyncio
async def test_update_task_status(client):
    #Создаём задачу
    create_resp = await client.post(
        "/tasks/",
        json={"title": "Patch test", "description": "Check PATCH endpoint"}
    )
    assert create_resp.status_code == 200
    created_task = create_resp.json()
    task_id = created_task["id"]

    #Обновляем статус
    patch_resp = await client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "In Progress"}
    )
    assert patch_resp.status_code == 200

    updated_task = patch_resp.json()
    assert updated_task["id"] == task_id
    assert updated_task["status"] == "In Progress"

    #Проверяем, что статус реально изменился в базе (через GET)
    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    task_data = get_resp.json()
    assert task_data["status"] == "In Progress"


@pytest.mark.asyncio
async def test_delete_task(client):
    #Создаём задачу
    create_resp = await client.post(
        "/tasks/",
        json={"title": "Delete me", "description": "Task to delete"}
    )
    assert create_resp.status_code == 200
    task = create_resp.json()
    task_id = task["id"]

    #Удаляем задачу
    delete_resp = await client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 200

    deleted_task = delete_resp.json()
    assert deleted_task["id"] == task_id
    assert deleted_task["title"] == "Delete me"

    #Проверяем, что задачи больше нет
    get_resp = await client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_file_full_lifecycle(client):
    """
    Полный сценарий работы с файлом:
    Создание задачи
    Загрузка файла
    Получение файла
    Удаление файла
    Проверка, что файл удалён
    """

    #Создаём задачу через board-service
    create_resp = await client.post(
        "/tasks/",
        json={"title": "Lifecycle test", "description": "Testing file lifecycle"}
    )
    assert create_resp.status_code == 200, f"Task creation failed: {create_resp.text}"
    task = create_resp.json()
    task_id = str(task["id"])

    test_task_id = f"{task_id}_lifecycle"

    #Загружаем файл в file-service
    file_content = b"Sample content for lifecycle test"
    test_file = io.BytesIO(file_content)

    async with httpx.AsyncClient() as real_client:
        upload_resp = await real_client.post(
            f"http://file-service:8001/files/{test_task_id}",
            files={"file": ("lifecycle.txt", test_file, "text/plain")}
        )

    assert upload_resp.status_code in (200, 201), f"Upload failed: {upload_resp.text}"
    upload_data = upload_resp.json()
    assert upload_data.get("filename") == "lifecycle.txt"
    assert "url" in upload_data

    #Получаем файл
    async with httpx.AsyncClient() as real_client:
        get_resp = await real_client.get(f"http://file-service:8001/files/{test_task_id}")

    assert get_resp.status_code == 200, f"File GET failed: {get_resp.text}"
    file_info = get_resp.json()
    assert file_info["filename"] == "lifecycle.txt"
    assert "url" in file_info

    #Удаляем файл
    async with httpx.AsyncClient() as real_client:
        delete_resp = await real_client.delete(f"http://file-service:8001/files/{test_task_id}")

    assert delete_resp.status_code == 200, f"File DELETE failed: {delete_resp.text}"

    #Проверяем, что теперь файл недоступен
    async with httpx.AsyncClient() as real_client:
        get_after_delete = await real_client.get(f"http://file-service:8001/files/{test_task_id}")

    assert get_after_delete.status_code == 404, "File should not exist after deletion"
