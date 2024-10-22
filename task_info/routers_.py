from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from task_info import crud_, schemas


router = APIRouter()


@router.post("/tasks/", response_model=schemas.Task)
def create_new_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = crud_.create_task(db=db, task=task)
    return db_task


@router.get("/tasks/{task_id}/", response_model=schemas.Task)
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    db_task = crud_.get_task(db=db, task_id=task_id)

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task
