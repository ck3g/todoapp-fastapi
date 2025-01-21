from fastapi import APIRouter, HTTPException, status

from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import Group

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_groups(current_user: UserDependency, session: SessionDep):
    groups = Group.all(session, user_id=current_user.id)

    return {"groups": groups}


@router.get("/{group_id}", status_code=status.HTTP_200_OK)
async def read_group(current_user: UserDependency, session: SessionDep, group_id: int):
    group = Group.find_by(session, user_id=current_user.id, obj_id=group_id)

    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    current_user: UserDependency, session: SessionDep, group_id: int
):
    group = Group.find_by(session, user_id=current_user.id, obj_id=group_id)

    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    group.destroy(session)
