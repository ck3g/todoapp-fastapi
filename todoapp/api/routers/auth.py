from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError
from sqlmodel import select

from todoapp.database.session import SessionDep
from todoapp.models.user import User
from todoapp.security.password import hash_password, verify_password
from todoapp.security.token import decode_token, encode_token

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    payload = decode_token(token)
    if payload == {}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return session.get(User, payload.get("user_id"))


UserDependency = Annotated[User, Depends(get_current_user)]


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

    # TODO: check whether user with this email and username already exists
    # TODO: username can overlap here, when user has the same email prefix. For example:
    # user@example.com and user@another-example.com
    user = User(email=request.email, username=username, hashed_password=hashed_password)
    session.add(user)
    session.commit()

    return {"access_token": encode_token(user), "token_type": "bearer"}


@router.post("/token", status_code=status.HTTP_200_OK)
async def create_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    email = form_data.username
    password = form_data.password
    user = session.exec(select(User).where(User.email == email)).first()

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return {"access_token": encode_token(user), "token_type": "bearer"}
