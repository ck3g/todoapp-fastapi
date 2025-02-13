from typing import Tuple

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import Group, User


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


class TestReadSingleGroup:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/groups/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(
            self,
            authenticated_client: Tuple[TestClient, User],
            create_group,
            create_list,
        ):
            client, current_user = authenticated_client
            group = create_group(user_id=current_user.id, title="Group title")
            create_list(user_id=current_user.id, group_id=group.id, title="List 1")
            create_list(user_id=current_user.id, group_id=group.id, title="List 2")

            response = client.get(f"/groups/{group.id}")

            assert response.status_code == status.HTTP_200_OK
            json_response = response.json()
            assert json_response == group.model_dump()
            assert len(json_response["task_lists"]) == 2

        def test_group_not_found(self, authenticated_client: Tuple[TestClient, User]):
            client, _current_user = authenticated_client

            response = client.get("/groups/503")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}


class TestCreateGroup:
    def test_unauthenticated(self, client: TestClient):
        response = client.post("/groups", json={"title": "New group"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(
            self, authenticated_client: Tuple[TestClient, User], session: Session
        ):
            client, current_user = authenticated_client
            response = client.post("/groups", json={"title": "New group"})

            groups = Group.all(session, user_id=current_user.id)

            assert len(groups) > 0
            group = groups[0]
            assert group is not None
            assert response.status_code == status.HTTP_201_CREATED
            json_response = response.json()
            assert json_response["id"] == group.id
            assert json_response["title"] == group.title
            assert group.user_id == current_user.id
            assert json_response == group.model_dump()

        def test_invalid_title(
            self, authenticated_client: Tuple[TestClient, User], session: Session
        ):
            client, current_user = authenticated_client
            response = client.post("/groups", json={"title": "G"})

            groups = Group.all(session, user_id=current_user.id)

            assert len(groups) == 0
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            json_response = response.json()
            assert json_response["detail"][0]["loc"] == ["body", "title"]
            assert (
                json_response["detail"][0]["msg"]
                == "String should have at least 3 characters"
            )


class TestDestroyGroup:
    def test_unauthenticated(self, client: TestClient):
        response = client.delete("/groups/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_group,
        ):
            client, current_user = authenticated_client
            group = create_group(user_id=current_user.id, title="Group title")

            response = client.delete(f"/groups/{group.id}")

            assert (
                Group.find_by(session, user_id=current_user.id, obj_id=group.id) is None
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

        def test_not_found(self, authenticated_client: Tuple[TestClient, User]):
            client, _current_user = authenticated_client

            response = client.delete("/groups/503")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}
