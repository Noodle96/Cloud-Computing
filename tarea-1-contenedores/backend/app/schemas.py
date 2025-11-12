from typing import List, Optional
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field("pending", pattern="^(pending|in_progress|done)$")
    tags: Optional[List[str]] = []

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|done)$")
    tags: Optional[List[str]] = None

class TaskOut(TaskBase):
    id: int
    class Config:
        from_attributes = True
