# scheduler/api/schemas.py
from datetime import datetime
from pydantic import BaseModel

class TaskCreate(BaseModel):
    command: str
    scheduled_at: datetime


class TaskRead(BaseModel):
    id: int
    command: str
    scheduled_at: datetime
    status: str
    created_at: datetime

    # Pydantic v2 replacement for orm_mode = True
    model_config = {"from_attributes": True}
