from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=List[schemas.TaskOut])
def list_tasks(status: Optional[str] = None, tag: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Task)
    if status:
        q = q.filter(models.Task.status == status)
    if tag:
        # q = q.filter(tag == any_(models.Task.tags))  # alternativa: models.Task.tags.any(tag) si usas SQLAlchemy 2
        q = q.filter(models.Task.tags.any(tag))  # <-- esta línea
    return q.order_by(models.Task.created_at.desc()).all()

@router.post("/", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    t = models.Task(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@router.get("/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    return t

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Task, task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    db.delete(t)
    db.commit()
