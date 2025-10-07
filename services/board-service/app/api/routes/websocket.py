from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# список активных подключений
active_connections: list[WebSocket] = []

@router.websocket("/board")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"Client connected: {len(active_connections)} total")

    try:
        while True:
            try:
                # ждём сообщение максимум 30 секунд
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                if data == "ping":
                    await websocket.send_text("pong")
                else:
                    print(f"Message from client: {data}")

            except asyncio.TimeoutError:
                # если клиент молчит — отправляем ping сами
                await websocket.send_text(json.dumps({"event": "ping"}))

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Client disconnected: {len(active_connections)} left")


# вспомогательная функция для рассылки
async def broadcast(message: dict):
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except Exception:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)
