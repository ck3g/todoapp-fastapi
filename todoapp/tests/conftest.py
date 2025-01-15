import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from todoapp.database.session import get_session
from todoapp.main import app
from todoapp.models import Task, TaskList, User
from todoapp.security.token import encode_token


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        # By not specifying the database name is enough to tell
        # SQLModel (actually SQLAlchemy) that we want to use
        # an in-memory SQLite database.
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
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


@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client: TestClient, create_user):
    user = create_user()
    token = encode_token(user)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client, user


@pytest.fixture(name="create_user", scope="function")
def create_user_fixture(session: Session):
    def _create_user(email="user@example.com", username="username", password="pwd123"):
        return User.create_by(
            session,
            email=email,
            username=username,
            password=password,
        )

    yield _create_user


@pytest.fixture(name="create_task")
def create_task_fixture(session: Session):
    def _create_task(user_id, title, completed=False, list_id=None, note=""):
        task = Task(
            user_id=user_id,
            list_id=list_id,
            title=title,
            completed=completed,
            note=note,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    yield _create_task


@pytest.fixture(name="create_list")
def create_list_fixture(session: Session):
    def _create_list(user_id, title):
        return TaskList.create_by(session, user_id=user_id, title=title)

    yield _create_list
