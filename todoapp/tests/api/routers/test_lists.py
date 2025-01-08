from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import TaskList


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
