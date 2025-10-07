from sqlalchemy import Column, String, DateTime, ForeignKey
from app.core.database import Base
from datetime import datetime
import uuid

class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
