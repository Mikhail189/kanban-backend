from fastapi import FastAPI
from app.api.routes import tasks, websocket
from app.core.database import Base, engine

app = FastAPI(title="Kanban Board Service")

app.include_router(tasks.router)
app.include_router(websocket.router)

# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok"}