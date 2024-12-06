from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from todoapp.models.user import User
from todoapp.security.token import decode_token

router = APIRouter(prefix="/tasks", tags=["tasks"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_token(token)
    if payload == {}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    # TODO: read a user from DB
    return User(email=payload.get("sub"), id=payload.get("user_id"))


UserDependency = Annotated[User, Depends(get_current_user)]


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
