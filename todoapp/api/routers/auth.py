from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from todoapp.api.models.auth import RegisterRequest
from todoapp.database.session import SessionDep
from todoapp.models.user import User
from todoapp.security.password import verify_password
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


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest, session: SessionDep):
    """Creates and new user with provided credentials"""
    if User.find_by_email(session, request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    if User.find_by_username(session, request.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    user = User.create_by(
        session,
        email=request.email,
        username=request.username,
        password=request.password,
    )

    return {"access_token": encode_token(user), "token_type": "bearer"}


@router.post("/token", status_code=status.HTTP_200_OK)
async def create_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    email_or_username = form_data.username
    password = form_data.password
    user = User.find_by_email_or_username(session, email_or_username)

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return {"access_token": encode_token(user), "token_type": "bearer"}
