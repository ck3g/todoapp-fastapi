from fastapi import APIRouter, HTTPException, status

from todoapp.api.models.list import ListRequest
from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import TaskList

router = APIRouter(prefix="/lists", tags=["lists"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_lists(current_user: UserDependency, session: SessionDep):
    lists = TaskList.all(session, user_id=current_user.id)

    return {"lists": lists}


@router.get("/{list_id}", status_code=status.HTTP_200_OK)
async def read_list(current_user: UserDependency, session: SessionDep, list_id: int):
    lst = TaskList.find_by(session, user_id=current_user.id, obj_id=list_id)

    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return lst


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_list(
    current_user: UserDependency, session: SessionDep, request: ListRequest
):
    lst = TaskList.create_by(session, title=request.title, user_id=current_user.id)

    return lst


@router.patch("/{list_id}", status_code=status.HTTP_200_OK)
async def update_list(
    current_user: UserDependency,
    session: SessionDep,
    request: ListRequest,
    list_id: int,
):
    lst = TaskList.find_by(session, user_id=current_user.id, obj_id=list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    attrs = request.model_dump(exclude_unset=True)
    lst = lst.update(session, **attrs)

    return lst


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(current_user: UserDependency, session: SessionDep, list_id: int):
    lst = TaskList.find_by(session, user_id=current_user.id, obj_id=list_id)
    if lst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    lst.destroy(session)
