from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterResponse(BaseModel):
    email: str
    username: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    password_confirmation: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest):
    username = request.email.split("@")[0]
    response = RegisterResponse(email=request.email, username=username)
    return {"msg": "User successfully created", "user": response}
