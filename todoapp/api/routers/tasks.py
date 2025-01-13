from fastapi import APIRouter, HTTPException, status

from todoapp.api.models.task import CreateTaskRequest, UpdateTaskRequest
from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import Task, TaskList

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_tasks(current_user: UserDependency, session: SessionDep):
    tasks = Task.all(session, user_id=current_user.id)

    return {"tasks": tasks}


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=Task)
async def read_task(current_user: UserDependency, session: SessionDep, task_id: int):
    task = Task.find_by(session, obj_id=task_id, user_id=current_user.id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return task


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Task)
async def create_task(
    current_user: UserDependency, session: SessionDep, request: CreateTaskRequest
):
    attrs = request.model_dump(exclude_unset=True)
    task_list = None
    if list_id := attrs.pop("list_id", None):
        task_list = TaskList.find_by(session, user_id=current_user.id, obj_id=list_id)

    return Task.create_by(
        session, user_id=current_user.id, task_list=task_list, **attrs
    )


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=Task)
async def update_task(
    current_user: UserDependency,
    session: SessionDep,
    task_id: int,
    request: UpdateTaskRequest,
):
    task = Task.find_by(session, obj_id=task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    attrs = request.model_dump(exclude_unset=True)
    task_list = None
    if list_id := attrs.pop("list_id", None):
        task_list = TaskList.find_by(session, obj_id=list_id, user_id=current_user.id)

    return task.update(session, task_list=task_list, **attrs)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(current_user: UserDependency, session: SessionDep, task_id: int):
    task = Task.find_by(session, obj_id=task_id, user_id=current_user.id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    task.destroy(session)
