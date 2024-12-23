from typing import Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import Task, User


@pytest.fixture(name="create_task")
def create_task_fixture(session: Session):
    def _create_task(user_id, title, completed=False):
        task = Task(user_id=user_id, title=title, completed=completed)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    yield _create_task


def test_read_tasks_unauthenticated(client: TestClient):
    response = client.get("/tasks")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_read_tasks_authenticated(
    authenticated_client: Tuple[TestClient, User], create_task, create_user
):
    client, current_user = authenticated_client

    another_user = create_user(
        email="another-user@example.com", username="another-user"
    )
    task1 = create_task(user_id=current_user.id, title="Task 1")
    task2 = create_task(user_id=current_user.id, title="Task 2", completed=True)
    create_task(user_id=another_user.id, title="Task 3")

    response = client.get("/tasks")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tasks": [
            task1.model_dump(),
            task2.model_dump(),
        ]
    }


def test_read_single_task_unauthenticated(client: TestClient):
    response = client.get("/tasks/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_read_single_task_autheticated(authenticated_client: TestClient, create_task):
    client, current_user = authenticated_client

    task = create_task(user_id=current_user.id, title="Task 1")

    response = client.get(f"/tasks/{task.id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == task.model_dump()


def test_read_single_task_authenticated_task_does_not_exist(
    authenticated_client: TestClient,
):
    client, _ = authenticated_client

    response = client.get("/tasks/1")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}


def test_read_single_task_authenticated_belongs_to_another_user(
    authenticated_client: TestClient, create_task, create_user
):
    client, _ = authenticated_client

    user = create_user(email="another-user@example.com", username="another-user")
    task = create_task(user_id=user.id, title="Another user task")

    response = client.get(f"/tasks/{task.id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}


def test_create_task_unauthenticated(client: TestClient):
    response = client.post("/tasks", json={"title": "New task"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_create_task_authenticated_success(
    authenticated_client: TestClient, session: Session
):
    client, current_user = authenticated_client
    response = client.post("/tasks", json={"title": "New task"})

    task = Task.all(session, user_id=current_user.id)[0]

    assert task is not None
    assert task.user_id == current_user.id
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == task.model_dump()


def test_create_task_authenticated_with_invalid_title(
    authenticated_client: TestClient, session: Session
):
    client, current_user = authenticated_client
    response = client.post("/tasks", json={"title": ""})

    tasks = Task.all(session, user_id=current_user.id)

    assert len(tasks) == 0
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    assert json_response["detail"][0]["loc"] == ["body", "title"]
    assert (
        json_response["detail"][0]["msg"] == "String should have at least 3 characters"
    )


def test_update_task_unauthenticated(client: TestClient):
    response = client.patch("/tasks/1", json={"title": "Updated title"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_update_task_authenticated(
    authenticated_client: TestClient, session: Session, create_task
):
    client, current_user = authenticated_client
    task = create_task(user_id=current_user.id, title="Task title")

    response = client.patch(
        f"/tasks/{task.id}", json={"title": "Updated title", "completed": True}
    )

    updated_task = Task.find_by(session, user_id=current_user.id, task_id=task.id)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_task.model_dump()
    assert updated_task.title == "Updated title"
    assert updated_task.completed


def test_update_task_authenticated_only_title(
    authenticated_client: TestClient, session: Session, create_task
):
    client, current_user = authenticated_client
    task = create_task(user_id=current_user.id, title="Task title")

    response = client.patch(f"/tasks/{task.id}", json={"title": "Updated title"})

    updated_task = Task.find_by(session, user_id=current_user.id, task_id=task.id)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_task.model_dump()
    assert updated_task.title == "Updated title"
    assert updated_task.completed == task.completed


def test_update_task_authenticated_another_user_task(
    authenticated_client: TestClient, session: Session, create_task, create_user
):
    client, _ = authenticated_client
    user = create_user(email="another-user@example.com", username="another-user")
    task = create_task(user_id=user.id, title="Another user task")

    response = client.patch(f"/tasks/{task.id}", json={"title": "Updated title"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}
    task = Task.find_by(session, task_id=task.id, user_id=user.id)
    assert task.title != "Updated title"


def test_update_task_authenticated_invalid_title(
    authenticated_client: TestClient, create_task
):
    client, current_user = authenticated_client
    task = create_task(user_id=current_user.id, title="Task title")

    response = client.patch(f"/tasks/{task.id}", json={"title": ""})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    assert json_response["detail"][0]["loc"] == ["body", "title"]
    assert (
        json_response["detail"][0]["msg"] == "String should have at least 3 characters"
    )


def test_delete_task_unauthenticated(client: TestClient):
    response = client.delete("/tasks/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_task_authenticated(
    authenticated_client: TestClient, session: Session, create_task
):
    client, current_user = authenticated_client
    task = create_task(user_id=current_user.id, title="To delete")

    tasks = Task.all(session)
    assert len(tasks) == 1

    response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    tasks = Task.all(session)
    assert len(tasks) == 0


def test_delete_task_authenticated_another_user_task(
    authenticated_client: TestClient, session: Session, create_task, create_user
):
    client, _ = authenticated_client
    user = create_user(email="another-user@example.com", username="another-user")
    task = create_task(user_id=user.id, title="Another user task")

    tasks = Task.all(session)
    assert len(tasks) == 1

    response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Not found"}
    tasks = Task.all(session)
    assert len(tasks) == 1
