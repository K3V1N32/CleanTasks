from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..auth import get_current_user
from ..ai import summarize_task, task_breakdown

# ---=== Initialize Router ===---
router = APIRouter()

def get_db():
    """
    Gives access to the database
    :return db: database object
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---=== CREATE TASK ===---
@router.post("/tasks")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    POST /tasks
    Creates a new task for the current user
    :param task:
    :param db:
    :param current_user:
    :return: dictionary containing task information
    """
    summary = summarize_task(task.title, task.description)
    breakdown = task_breakdown(task.title, task.description)

    db_task = models.Task(
        title=task.title,
        description=task.description,
        owner_id=current_user.id,
        ai_summary=summary,
        ai_breakdown="|".join(breakdown['subtasks'])
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ---=== GET ALL TASKS FOR CURRENT USER ===---
@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    GET /tasks
    Retrieves a list of all tasks for current user
    :param db:
    :param current_user:
    :return: list containing task objects
    """
    return db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()

# ---=== UPDATE TASK ===---
@router.put("/tasks/{task_id}")
def update_task(task_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    PUT /tasks/{task_id}
    Updates a task based on task_id for the current user
    :param task_id:
    :param task:
    :param db:
    :param current_user:
    :return:
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id,models.Task.owner_id == current_user.id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_task.title = task.title
    db_task.description = task.description
    db_task.ai_summary = summarize_task(task.title, task.description)
    db_task.ai_breakdown = "|".join(task_breakdown(task.title, task.description)['subtasks'])

    db.commit()
    return db_task

# ---=== REGENERATE AI ===---
@router.post("/tasks/{task_id}/regenerate-ai")
def regenerate_ai(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    POST /tasks/{task_id}/regenerate-ai
    Regenerates the AI in a task for the current user
    :param task_id:
    :param db:
    :param current_user:
    :return: simple message that AI was regenerated into the database
    """
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.ai_summary = summarize_task(task.title, task.description)
    task.ai_breakdown = "|".join(task_breakdown(task.title, task.description)['subtasks'])

    db.commit()

    return {"message": "AI regenerated"}

# ---=== DELETE TASK ===---
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    DELETE /tasks/{task_id}
    Deletes a task for the current user at {task_id}
    :param task_id:
    :param db:
    :return: {message:Task deleted} if successful, else {error:Task not found}
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted"}
    return {"error": "Task not found"}

# ---=== AI SUMMERIZE ===---
@router.post("/tasks/{task_id}/summarize")
def summarize_task_endpoint(
        task_id: int,
        db: Session = Depends(get_db),
        current_user = Depends(get_current_user)
):
    """
    POST /tasks/{task_id}/summarize
    Uses local llama3 AI Agent to summarize a task
    :param task_id:
    :param db:
    :param current_user:
    :return: the original task and the generated summary
    """
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    summary = summarize_task(task.title, task.description)

    return {
        "original": {
            "title": task.title,
            "description": task.description,
        },
        "ai_summary": summary
    }

# ---=== AI BREAKDOWN ===---
@router.post("/tasks/{task_id}/subtask")
def subtask_breakdown(task_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    POST /tasks/{task_id}/subtask
    Use local llama3 AI to break down the task into subtasks
    :param task_id:
    :param db:
    :param current_user:
    :return: the original task and the generated subtasks
    """
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "original": { "task": task.title, "description": task.description},
        "breakdown": task_breakdown(task.title, task.description)
    }