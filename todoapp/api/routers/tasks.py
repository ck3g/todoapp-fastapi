from fastapi import APIRouter, status
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
async def read_task(task_id: int):
    return {"id": task_id, "title": f"Task {task_id}"}
