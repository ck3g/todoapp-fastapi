from fastapi import status
from fastapi.testclient import TestClient


def test_task_lists_unauthenticated(client: TestClient):
    response = client.get("/tasks")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_task_list_authenticated(authenticated_client: TestClient):
    response = authenticated_client.get("/tasks")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tasks_for_user@example.com": [
            {"id": 1, "title": "Task 1"},
            {"id": 2, "title": "Task 2"},
        ]
    }
