from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import TaskList

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_lists(current_user: UserDependency, session: SessionDep):
    lists = TaskList.all(session, user_id=current_user.id)

    return {"lists": lists}


class ListRequest(BaseModel):
    title: Optional[str] = Field(min_length=3, max_length=50)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_list(
    current_user: UserDependency, session: SessionDep, request: ListRequest
):
    lst = TaskList.create_by(session, title=request.title, user_id=current_user.id)

    return lst
