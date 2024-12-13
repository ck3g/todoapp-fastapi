from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import Task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_tasks(current_user: UserDependency, session: SessionDep):
    results = Task.all(session, user_id=current_user.id)
    tasks = []
    for task in results:
        tasks.append({"id": task.id, "title": task.title})

    return {"tasks": tasks}


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def read_task(current_user: UserDependency, session: SessionDep, task_id: int):
    task = Task.find_by(session, task_id=task_id, user_id=current_user.id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return {"id": task.id, "title": task.title}


class TaskRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    current_user: UserDependency, session: SessionDep, request: TaskRequest
):
    task = Task.create_by(session, title=request.title, user_id=current_user.id)

    return {"id": task.id, "title": task.title}
