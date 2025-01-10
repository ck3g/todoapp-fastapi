from datetime import date
from typing import Tuple

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from todoapp.models import Task, User


class TestReadTasks:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/tasks")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    def test_authenticated_success(
        self, authenticated_client: Tuple[TestClient, User], create_task, create_user
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


class TestReadSingleTask:
    def test_unauthenticated(self, client: TestClient):
        response = client.get("/tasks/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(self, authenticated_client: TestClient, create_task):
            client, current_user = authenticated_client

            task = create_task(user_id=current_user.id, title="Task 1")

            response = client.get(f"/tasks/{task.id}")

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == task.model_dump()

        def test_task_does_not_exist(
            self,
            authenticated_client: TestClient,
        ):
            client, _ = authenticated_client

            response = client.get("/tasks/1")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}

        def test_belongs_to_another_user(
            self, authenticated_client: TestClient, create_task, create_user
        ):
            client, _ = authenticated_client

            user = create_user(
                email="another-user@example.com", username="another-user"
            )
            task = create_task(user_id=user.id, title="Another user task")

            response = client.get(f"/tasks/{task.id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}


class TestCreateTask:
    def test_unauthenticated(self, client: TestClient):
        response = client.post("/tasks", json={"title": "New task"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(self, authenticated_client: TestClient, session: Session):
            client, current_user = authenticated_client
            response = client.post(
                "/tasks", json={"title": "New task", "note": "Task note"}
            )

            task = Task.all(session, user_id=current_user.id)[0]

            assert task is not None
            assert task.user_id == current_user.id
            assert task.list_id is None
            assert task.title == "New task"
            assert task.note == "Task note"
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json() == task.model_dump()

        def test_with_due_date_success(
            self, authenticated_client: TestClient, session: Session
        ):
            client, current_user = authenticated_client
            response = client.post(
                "/tasks", json={"title": "New task", "due_date": "2015-01-06"}
            )

            task = Task.all(session, user_id=current_user.id)[0]

            assert task is not None
            assert task.user_id == current_user.id
            assert task.title == "New task"
            assert task.due_date == date(2015, 1, 6)
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json() == task.model_dump()

        def test_with_list_id_success(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_list,
        ):
            client, current_user = authenticated_client
            lst = create_list(user_id=current_user.id, title="List 1")

            response = client.post(
                "/tasks", json={"title": "New task", "list_id": lst.id}
            )

            tasks = Task.all(session, user_id=current_user.id)

            assert len(tasks) == 1
            task = tasks[0]
            assert task.user_id == current_user.id
            assert task.title == "New task"
            assert task.list_id == lst.id
            assert response.status_code == status.HTTP_201_CREATED
            json_response = response.json()
            assert json_response == task.model_dump()
            assert json_response["list_id"] == lst.id

        def test_with_invalid_title(
            self, authenticated_client: TestClient, session: Session
        ):
            client, current_user = authenticated_client
            response = client.post("/tasks", json={"title": ""})

            tasks = Task.all(session, user_id=current_user.id)

            assert len(tasks) == 0
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            json_response = response.json()
            assert json_response["detail"][0]["loc"] == ["body", "title"]
            assert (
                json_response["detail"][0]["msg"]
                == "String should have at least 3 characters"
            )

        def test_with_invalid_due_date(
            self, authenticated_client: TestClient, session: Session
        ):
            client, current_user = authenticated_client
            response = client.post(
                "/tasks", json={"title": "New task", "due_date": "Invalid"}
            )

            tasks = Task.all(session, user_id=current_user.id)

            assert len(tasks) == 0
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            json_response = response.json()
            assert json_response["detail"][0]["loc"] == ["body", "due_date"]
            assert (
                json_response["detail"][0]["msg"]
                == "Value error, Invalid date format. Please use YYYY-MM-DD."
            )

        def test_with_list_id_of_another_user(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_user,
            create_list,
        ):
            client, current_user = authenticated_client

            user = create_user(email="user2@example.com", username="user2")
            lst = create_list(user_id=user.id, title="Another user list")

            response = client.post(
                "/tasks", json={"title": "New task", "list_id": lst.id}
            )

            tasks = Task.all(session, user_id=current_user.id)

            assert len(tasks) == 0
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert response.json() == {"detail": "List does not exist"}


class TestUpdateTask:
    def test_unauthenticated(self, client: TestClient):
        response = client.patch("/tasks/1", json={"title": "Updated title"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(
            self, authenticated_client: TestClient, session: Session, create_task
        ):
            client, current_user = authenticated_client
            task = create_task(user_id=current_user.id, title="Task title")

            response = client.patch(
                f"/tasks/{task.id}",
                json={
                    "title": "Updated title",
                    "completed": True,
                    "note": "Updated note",
                    "due_date": "2025-01-07",
                },
            )

            updated_task = Task.find_by(
                session, user_id=current_user.id, obj_id=task.id
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == updated_task.model_dump()
            assert updated_task.title == "Updated title"
            assert updated_task.note == "Updated note"
            assert updated_task.due_date == date(2025, 1, 7)
            assert updated_task.completed

        def test_only_title(
            self, authenticated_client: TestClient, session: Session, create_task
        ):
            client, current_user = authenticated_client
            task = create_task(user_id=current_user.id, title="Task title")

            response = client.patch(
                f"/tasks/{task.id}", json={"title": "Updated title"}
            )

            updated_task = Task.find_by(
                session, user_id=current_user.id, obj_id=task.id
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == updated_task.model_dump()
            assert updated_task.title == "Updated title"
            assert updated_task.completed == task.completed

        def test_only_list_id(
            self,
            authenticated_client: Tuple[TestClient, User],
            session: Session,
            create_list,
            create_task,
        ):
            client, current_user = authenticated_client
            task = create_task(user_id=current_user.id, title="Task title")
            lst = create_list(user_id=current_user.id, title="List title")

            response = client.patch(f"/tasks/{task.id}", json={"list_id": lst.id})

            updated_task = Task.find_by(
                session, user_id=current_user.id, obj_id=task.id
            )
            json_response = response.json()

            assert response.status_code == status.HTTP_200_OK
            assert json_response == updated_task.model_dump()
            assert json_response["list_id"] == lst.id
            assert updated_task.list_id == lst.id

        def test_another_user_task(
            self,
            authenticated_client: TestClient,
            session: Session,
            create_task,
            create_user,
        ):
            client, _ = authenticated_client
            user = create_user(
                email="another-user@example.com", username="another-user"
            )
            task = create_task(user_id=user.id, title="Another user task")

            response = client.patch(
                f"/tasks/{task.id}", json={"title": "Updated title"}
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}
            task = Task.find_by(session, obj_id=task.id, user_id=user.id)
            assert task.title != "Updated title"

        def test_another_user_list(
            self,
            authenticated_client: Tuple[TestClient, User],
            create_task,
            create_user,
            create_list,
        ):
            client, current_user = authenticated_client
            task = create_task(user_id=current_user.id, title="Task title")
            user = create_user(email="user2@example.com", username="user2")
            lst = create_list(user_id=user.id, title="List 1")

            response = client.patch(f"/tasks/{task.id}", json={"list_id": lst.id})

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            assert response.json() == {"detail": "List does not exist"}

        def test_invalid_title(self, authenticated_client: TestClient, create_task):
            client, current_user = authenticated_client
            task = create_task(user_id=current_user.id, title="Task title")

            response = client.patch(f"/tasks/{task.id}", json={"title": ""})

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            json_response = response.json()
            assert json_response["detail"][0]["loc"] == ["body", "title"]
            assert (
                json_response["detail"][0]["msg"]
                == "String should have at least 3 characters"
            )


class TestDeleteTask:
    def test_unauthenticated(self, client: TestClient):
        response = client.delete("/tasks/1")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Not authenticated"}

    class TestAuthenticated:
        def test_success(
            self, authenticated_client: TestClient, session: Session, create_task
        ):
            client, current_user = authenticated_client
            task = create_task(user_id=current_user.id, title="To delete")

            tasks = Task.all(session)
            assert len(tasks) == 1

            response = client.delete(f"/tasks/{task.id}")

            assert response.status_code == status.HTTP_204_NO_CONTENT
            tasks = Task.all(session)
            assert len(tasks) == 0

        def test_another_user_task(
            self,
            authenticated_client: TestClient,
            session: Session,
            create_task,
            create_user,
        ):
            client, _ = authenticated_client
            user = create_user(
                email="another-user@example.com", username="another-user"
            )
            task = create_task(user_id=user.id, title="Another user task")

            tasks = Task.all(session)
            assert len(tasks) == 1

            response = client.delete(f"/tasks/{task.id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.json() == {"detail": "Not found"}
            tasks = Task.all(session)
            assert len(tasks) == 1
