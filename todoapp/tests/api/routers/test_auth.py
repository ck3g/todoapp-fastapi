from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
import pytest

from todoapp.main import app
from todoapp.database.session import get_session
from todoapp.models.user import User


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

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "msg": "User successfully created",
        "user": {"id": user.id, "email": "user@example.com", "username": "user"},
    }


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
