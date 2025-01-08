from typing import Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import TaskList, User


@pytest.fixture(name="create_list")
def create_list_fixture(session: Session):
    def _create_list(user_id, title):
        return TaskList.create_by(session, user_id=user_id, title=title)

    yield _create_list


def test_read_lists_unauthenticated(client: TestClient):
    response = client.get("/lists")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_read_lists_authenticated(
    authenticated_client: Tuple[TestClient, User], create_list, create_user
):
    client, current_user = authenticated_client

    another_user = create_user(
        email="another-user@example.com", username="another-user"
    )
    list1 = create_list(user_id=current_user.id, title="List 1")
    list2 = create_list(user_id=current_user.id, title="List 2")
    create_list(user_id=another_user.id, title="List 3")

    response = client.get("/lists")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "lists": [
            list1.model_dump(),
            list2.model_dump(),
        ]
    }


def test_create_list_unauthenticated(client: TestClient):
    response = client.post("/lists", json={"title": "New list"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_create_list_authenticated(authenticated_client: TestClient, session: Session):
    client, current_user = authenticated_client
    response = client.post("/lists", json={"title": "New list"})

    lists = TaskList.all(session, user_id=current_user.id)

    assert len(lists) > 0
    lst = lists[0]
    assert lst is not None
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response["id"] == lst.id
    assert json_response["title"] == lst.title
    assert lst.user_id == current_user.id
    assert response.json() == lst.model_dump()


def test_create_list_authenticated_with_invalid_title(
    authenticated_client: TestClient, session: Session
):
    client, current_user = authenticated_client
    response = client.post("/lists", json={"title": "L"})

    lists = TaskList.all(session, user_id=current_user.id)

    assert len(lists) == 0
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    assert json_response["detail"][0]["loc"] == ["body", "title"]
    assert (
        json_response["detail"][0]["msg"] == "String should have at least 3 characters"
    )
