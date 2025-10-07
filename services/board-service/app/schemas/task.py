from pydantic import BaseModel
from enum import Enum

class TaskStatus(str, Enum):
    todo = "To Do"
    in_progress = "In Progress"
    done = "Done"

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo


class TaskCreate(TaskBase):
    pass


class TaskUpdateStatus(BaseModel):
    status: TaskStatus


class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    file: dict | None = None

    class Config:
        from_attributes = True
