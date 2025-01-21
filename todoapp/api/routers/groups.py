from fastapi import APIRouter, status

from todoapp.api.routers.auth import UserDependency
from todoapp.database.session import SessionDep
from todoapp.models import Group

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_groups(current_user: UserDependency, session: SessionDep):
    groups = Group.all(session, user_id=current_user.id)

    return {"groups": groups}
