from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import Task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_tasks(current_user: UserDependency, session: SessionDep):
    results = session.exec(select(Task).where(Task.user_id == current_user.id))
    tasks = []
    for task in results:
        tasks.append({"id": task.id, "title": task.title})

    return {"tasks": tasks}


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def read_task(current_user: UserDependency, session: SessionDep, task_id: int):
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    ).first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return {"id": task.id, "title": task.title}
