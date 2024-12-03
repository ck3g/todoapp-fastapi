from fastapi import APIRouter, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError

from todoapp.database.session import SessionDep
from todoapp.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated=["auto"])


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


def hash_password(password) -> str:
    """Hashes the password"""
    return pwd_context.hash(password)


def verify_password(password, hashed_password) -> bool:
    """Return False when password verifycation fails"""
    try:
        return pwd_context.verify(password, hashed_password)
    except ValueError:
        return False
