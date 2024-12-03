from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError
from sqlmodel import select

from todoapp.database.session import SessionDep
from todoapp.models.user import User
from todoapp.security.password import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterResponse(BaseModel):
    id: int
    email: str
    username: str


class RegisterRequest(BaseModel):
    """Create user request form"""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=3, max_length=255)
    password_confirmation: str = Field(min_length=3, max_length=255)

    @model_validator(mode="after")
    def validate_password_and_confirmation(self):
        """Validates whether password matches password_confirmation"""
        p = self.password
        pc = self.password_confirmation
        if p is not None and pc is not None and p != pc:
            raise PydanticCustomError(
                "confirmation_error", "Password and Password Confirmation do not match"
            )

        return self


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest, session: SessionDep):
    """Creates and new user with provided credentials"""
    username = request.email.split("@")[0]
    hashed_password = hash_password(request.password)

    user = User(email=request.email, username=username, hashed_password=hashed_password)
    session.add(user)
    session.commit()

    response = RegisterResponse(id=user.id, email=user.email, username=user.username)
    return {"msg": "User successfully created", "user": response}


class TokenRequest(BaseModel):
    email: str
    password: str


@router.post("/token", status_code=status.HTTP_200_OK)
async def create_token(request: TokenRequest, session: SessionDep):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return {"token": "fake-token"}
