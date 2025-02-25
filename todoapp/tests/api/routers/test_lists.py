import logging
from typing import Tuple

import pytest
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
        self,
        authenticated_client: Tuple[TestClient, User],
        create_list,
        create_user,
        create_task,
    ):
        client, current_user = authenticated_client

        another_user = create_user(
            email="another-user@example.com", username="another-user"
        )
        list1 = create_list(user_id=current_user.id, title="List 1")
        list2 = create_list(user_id=current_user.id, title="List 2")
        create_list(user_id=another_user.id, title="List 3")
        create_task(user_id=current_user.id, list_id=list1.id, title="Task 1")
        create_task(user_id=current_user.id, list_id=list1.id, title="Task 2")
        create_task(user_id=current_user.id, list_id=list2.id, title="Task 3")

        response = client.get("/lists")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "lists": [
                list1.model_dump(),
                list2.model_dump(),
            ]
        }

    @pytest.mark.skip(reason="Fixing N+1 problems seems to be pain in the ass")
    def test_authenticated_n_plus_one(
        self,
        caplog,
        authenticated_client: Tuple[TestClient, User],
        create_list,
        create_user,
        create_task,
    ):
        client, current_user = authenticated_client

        another_user = create_user(
            email="another-user@example.com", username="another-user"
        )
        list1 = create_list(user_id=current_user.id, title="List 1")
        list2 = create_list(user_id=current_user.id, title="List 2")
        create_list(user_id=another_user.id, title="List 3")
        create_task(user_id=current_user.id, list_id=list1.id, title="Task 1")
        create_task(user_id=current_user.id, list_id=list1.id, title="Task 2")
        create_task(user_id=current_user.id, list_id=list2.id, title="Task 3")
        create_task(user_id=current_user.id, list_id=list2.id, title="Task 4")
        create_task(user_id=current_user.id, list_id=list2.id, title="Task 5")

        with caplog.at_level(logging.INFO):
            response = client.get("/lists")

        assert response.status_code == status.HTTP_200_OK

        # Test N+1 problem
        query_logs = [record for record in caplog.records if "SELECT" in record.message]
        print("\n+++++++\n".join(record.message for record in query_logs))
        assert len(query_logs) == 2


class TestReadSingleList:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/lists/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    class TestAuthenticated:
        def test_success(
            self,
            authenticated_client: Tuple[TestClient, User],
            create_list,
            create_task,
        ):
            client, current_user = authenticated_client

            lst = create_list(user_id=current_user.id, title="List 1")
            create_task(user_id=current_user.id, list_id=lst.id, title="Task 1")
            create_task(user_id=current_user.id, list_id=lst.id, title="Task 2")

            response = client.get(f"/lists/{lst.id}")

            assert response.status_code == status.HTTP_200_OK
            json_response = response.json()
            assert json_response == lst.model_dump()
            assert len(json_response["tasks"]) == 2

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
        def test_success(
            self, authenticated_client: Tuple[TestClient, User], session: Session
        ):
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

        def test_with_group_id_success(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_group,
        ):
            client, current_user = authenticated_client
            group = create_group(user_id=current_user.id, title="Group 1")

            response = client.post(
                "/lists", json={"title": "New list", "group_id": group.id}
            )

            lists = TaskList.all(session, user_id=current_user.id)

            assert len(lists) == 1
            lst = lists[0]
            assert lst.user_id == current_user.id
            assert lst.title == "New list"
            assert lst.group_id == group.id
            assert response.status_code == status.HTTP_201_CREATED
            json_response = response.json()
            assert json_response == lst.model_dump()
            assert json_response["group"] == {"id": group.id, "title": group.title}

        def test_with_group_id_of_another_user(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_user,
            create_group,
        ):
            client, current_user = authenticated_client

            user = create_user(email="user2@example.com", username="user2")
            group = create_group(user_id=user.id, title="Another user group")

            response = client.post(
                "/lists", json={"title": "New list", "group_id": group.id}
            )

            lists = TaskList.all(session, user_id=current_user.id)

            assert len(lists) == 1
            lst = lists[0]
            assert response.status_code == status.HTTP_201_CREATED
            json_response = response.json()
            assert json_response == lst.model_dump()
            assert json_response["title"] == "New list"
            assert json_response["group"] is None


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

        def test_only_group_id(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_list,
            create_group,
        ):
            client, current_user = authenticated_client
            lst = create_list(user_id=current_user.id, title="List title")
            group = create_group(user_id=current_user.id, title="Group title")

            response = client.patch(f"/lists/{lst.id}", json={"group_id": group.id})

            updated_list = TaskList.find_by(
                session, user_id=current_user.id, obj_id=lst.id
            )
            json_response = response.json()

            assert response.status_code == status.HTTP_200_OK
            assert json_response == updated_list.model_dump()
            assert json_response["group"] == {"id": group.id, "title": group.title}
            assert updated_list.group_id == group.id

        def test_another_user_group(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_list,
            create_group,
            create_user,
        ):
            client, current_user = authenticated_client
            lst = create_list(user_id=current_user.id, title="List title")
            user = create_user(email="user2@example.com", username="user2")
            group = create_group(user_id=user.id, title="Another user group")
            original_group_id = lst.group_id

            response = client.patch(f"/lists/{lst.id}", json={"group_id": group.id})

            session.refresh(lst)

            assert response.status_code == status.HTTP_200_OK
            assert lst.group_id == original_group_id


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
