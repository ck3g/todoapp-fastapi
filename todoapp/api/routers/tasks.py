from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import Task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_tasks(current_user: UserDependency, session: SessionDep):
    tasks = Task.all(session, user_id=current_user.id)

    return {"tasks": tasks}


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=Task)
async def read_task(current_user: UserDependency, session: SessionDep, task_id: int):
    task = Task.find_by(session, task_id=task_id, user_id=current_user.id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return task


class TaskRequest(BaseModel):
    title: Optional[str] = Field(min_length=3, max_length=255)
    completed: Optional[bool] = None


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Task)
async def create_task(
    current_user: UserDependency, session: SessionDep, request: TaskRequest
):
    task = Task.create_by(session, title=request.title, user_id=current_user.id)

    return task


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=Task)
async def update_task(
    current_user: UserDependency,
    session: SessionDep,
    task_id: int,
    request: TaskRequest,
):
    task = Task.find_by(session, task_id=task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    attrs = request.model_dump(exclude_unset=True)
    task = task.update(session, **attrs)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(current_user: UserDependency, session: SessionDep, task_id: int):
    task = Task.find_by(session, task_id=task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    task.destroy(session)
