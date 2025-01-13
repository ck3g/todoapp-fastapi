from typing import Tuple

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import TaskList, User


class TestReadLists:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/lists")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    def test_authenticated_success(
        self, authenticated_client: Tuple[TestClient, User], create_list, create_user
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


class TestReadSingleList:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/lists/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    class TestAuthenticated:
        def test_success(
            self, authenticated_client: Tuple[TestClient, User], create_list
        ):
            client, current_user = authenticated_client

            lst = create_list(user_id=current_user.id, title="List 1")

            response = client.get(f"/lists/{lst.id}")

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == lst.model_dump()

        def test_belongs_to_another_user(
            self,
            authenticated_client: Tuple[TestClient, User],
            create_user,
            create_list,
        ):
            client, _current_user = authenticated_client

            user = create_user(email="user2@example.com", username="user2")
            lst = create_list(user_id=user.id, title="List 1")

            response = client.get(f"/lists/{lst.id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}


class TestCreateList:
    def test_unauthenticated(self, client: TestClient):
        response = client.post("/lists", json={"title": "New list"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(self, authenticated_client: TestClient, session: Session):
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

        def test_with_invalid_title(
            self, authenticated_client: Tuple[TestClient, User], session: Session
        ):
            client, current_user = authenticated_client
            response = client.post("/lists", json={"title": "L"})

            lists = TaskList.all(session, user_id=current_user.id)

            assert len(lists) == 0
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            json_response = response.json()
            assert json_response["detail"][0]["loc"] == ["body", "title"]
            assert (
                json_response["detail"][0]["msg"]
                == "String should have at least 3 characters"
            )


class TestUpdateList:
    def test_unauthenticated(self, client: TestClient):
        response = client.patch("/lists/1", json={"title": "Updated title"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    class TestAuthenticated:
        def test_success(
            self, authenticated_client: Tuple[TestClient, User], create_list
        ):
            client, current_user = authenticated_client

            lst = create_list(user_id=current_user.id, title="List title")

            response = client.patch(f"/lists/{lst.id}", json={"title": "Updated title"})

            assert lst.title == "Updated title"
            assert response.status_code == status.HTTP_200_OK
            json_response = response.json()
            assert json_response == lst.model_dump()
            assert json_response["title"] == "Updated title"

        def test_blongs_to_another_user(
            self,
            authenticated_client: Tuple[TestClient, User],
            create_list,
            create_user,
        ):
            client, _current_user = authenticated_client

            user = create_user(email="user2@example.com", username="user2")
            lst = create_list(user_id=user.id, title="List title")

            response = client.patch(f"/lists/{lst.id}", json={"title": "Updated title"})

            assert lst.title == "List title"
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}

        def test_invalid_title(
            self, authenticated_client: Tuple[TestClient, User], create_list
        ):
            client, current_user = authenticated_client

            lst = create_list(user_id=current_user.id, title="List title")

            response = client.patch(f"/lists/{lst.id}", json={"title": "L"})

            assert lst.title == "List title"
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            json_response = response.json()
            assert json_response["detail"][0]["loc"] == ["body", "title"]
            assert (
                json_response["detail"][0]["msg"]
                == "String should have at least 3 characters"
            )


class TestDeleteList:
    def test_unauthenticated(self, client: TestClient):
        response = client.delete("/lists/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    class TestAuthenticated:
        def test_success(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_list,
        ):
            client, current_user = authenticated_client

            lst = create_list(user_id=current_user.id, title="List title")

            response = client.delete(f"/lists/{lst.id}")

            assert (
                TaskList.find_by(session, user_id=current_user.id, obj_id=lst.id)
                is None
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

        def test_belongs_to_another_user(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_list,
            create_user,
        ):
            client, _current_user = authenticated_client

            user = create_user(email="user2@example.com", username="user2")
            lst = create_list(user_id=user.id, title="List title")

            response = client.delete(f"/lists/{lst.id}")

            assert TaskList.find_by(session, user_id=user.id, obj_id=lst.id) is not None
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}
