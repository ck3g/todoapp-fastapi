from typing import Tuple

from fastapi import status
from fastapi.testclient import TestClient

from todoapp.models import User


class TestReadGroups:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/groups")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    def test_authenticated_success(
        self,
        authenticated_client: Tuple[TestClient, User],
        create_user,
        create_group,
    ):
        client, current_user = authenticated_client

        another_user = create_user(email="user2@example.com", username="user2")
        group1 = create_group(user_id=current_user.id, title="Group 1")
        group2 = create_group(user_id=current_user.id, title="Group 2")
        _group3 = create_group(user_id=another_user.id, title="Group 3")

        response = client.get("/groups")
        assert response.json() == {
            "groups": [
                group1.model_dump(),
                group2.model_dump(),
            ]
        }
