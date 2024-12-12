from typing import Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import Task, User


@pytest.fixture(name="create_task")
def create_task_fixture(session: Session):
    def _create_task(user_id, title):
        task = Task(user_id=user_id, title=title)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    yield _create_task


def test_task_lists_unauthenticated(client: TestClient):
    response = client.get("/tasks")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_task_list_authenticated(
    authenticated_client: Tuple[TestClient, User], create_task, create_user
):
    client, current_user = authenticated_client

    another_user = create_user(
        email="another-user@example.com", username="another-user"
    )
    task1 = create_task(user_id=current_user.id, title="Task 1")
    task2 = create_task(user_id=current_user.id, title="Task 2")
    create_task(user_id=another_user.id, title="Task 3")

    response = client.get("/tasks")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tasks": [
            {"id": task1.id, "title": task1.title},
            {"id": task2.id, "title": task2.title},
        ]
    }
