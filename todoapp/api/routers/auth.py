from fastapi import APIRouter, status

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user():
    return {"msg": "User successfully created"}
