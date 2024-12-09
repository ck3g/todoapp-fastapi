from fastapi import APIRouter, status

from todoapp.api.routers.auth import UserDependency

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_tasks(current_user: UserDependency):
    return {
        f"tasks_for_{current_user.email}": [
            {"id": 1, "title": "Task 1"},
            {"id": 2, "title": "Task 2"},
        ]
    }


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def read_task(task_id: int):
    return {"id": task_id, "title": f"Task {task_id}"}
