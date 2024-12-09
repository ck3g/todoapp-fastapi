import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from todoapp.api.routers.auth import get_current_user, oauth2_scheme
from todoapp.database.session import get_session
from todoapp.main import app
from todoapp.models.user import User
from todoapp.security.password import hash_password, verify_password
from todoapp.security.token import decode_token, encode_token


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        # By not specifying the database name is enough to tell
        # SQLModel (actually SQLAlchemy) that we want to use
        # an in-memory SQLite database.
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def is_valid_jwt_token(user: User, token: str) -> bool:
    if token is None:
        return False

    token_data = decode_token(token)
    return token_data["sub"] == user.email and token_data["user_id"] == user.id


def test_auth_register_successful_response(session: Session, client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "pwd123",
            "password_confirmation": "pwd123",
        },
    )

    user = session.exec(select(User)).first()
    assert user is not None
    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.username == "user"
    assert verify_password(
        "pwd123", user.hashed_password
    ), "cannot verify hashed password"

    json_response = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert json_response["token_type"] == "bearer"
    assert is_valid_jwt_token(user, json_response["access_token"])


@pytest.mark.parametrize(
    "email, password, password_confirmation, expected_type, expected_msg",
    [
        (
            "e",
            "pass123",
            "pass123",
            "string_too_short",
            "String should have at least 3 characters",
        ),
        (
            "email@example.com",
            "p",
            "p",
            "string_too_short",
            "String should have at least 3 characters",
        ),
        (
            "email@example.com",
            "pass123",
            "pass123456",
            "confirmation_error",
            "Password and Password Confirmation do not match",
        ),
    ],
    ids=[
        "email_string_too_short",
        "password_string_too_short",
        "password_and_confirmation_do_not_match",
    ],
)
def test_auth_register_validation_errors(
    client: TestClient,
    email,
    password,
    password_confirmation,
    expected_type,
    expected_msg,
):
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "password_confirmation": password_confirmation,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    for err in json_response["detail"]:
        assert expected_type == err["type"]
        assert expected_msg == err["msg"]


@pytest.mark.parametrize(
    "email, password, persisted_user, expect_error",
    [
        ("user@example.com", "pwd123", True, False),
        ("user@example.com", "wrong-pwd", True, True),
        ("user@example.com", "pwd123", False, True),
    ],
    ids=["valid credentials", "invalid credentials", "no user"],
)
def test_auth_create_token(
    client: TestClient,
    session: Session,
    email,
    password,
    persisted_user,
    expect_error,
):
    if persisted_user:
        # Create user in DB
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=hash_password("pwd123"),
        )
        session.add(user)
        session.commit()

    response = client.post(
        "/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if expect_error:
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Invalid email or password"}
    else:
        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()
        assert json_response["token_type"] == "bearer"
        assert is_valid_jwt_token(user, json_response["access_token"])


@pytest.mark.asyncio
async def test_get_current_user_valid_token_and_existing_user(session: Session):
    user = User(
        email="user1@example.com",
        username="user1",
        hashed_password=hash_password("pwd123"),
    )
    session.add(user)
    session.commit()

    token = encode_token(user)
    result = await get_current_user(token, session)

    assert result == user


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(session: Session):
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", session)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_get_current_user_valid_token_user_does_not_exist(session: Session):
    non_peristed_user = User(email="user@example.com", user_id=503)
    token = encode_token(non_peristed_user)
    result = await get_current_user(token, session)

    assert result is None
