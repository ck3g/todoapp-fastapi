from sqlmodel import Session

from todoapp.models import Task, TaskList


def test_task_list_destroy(session: Session, create_user, create_list, create_task):
    user = create_user(email="user@example.com", username="user")
    task_list = create_list(user_id=user.id, title="List title")
    task1 = create_task(user_id=user.id, title="Task 1")
    task2 = create_task(user_id=user.id, list_id=task_list.id, title="Task 2")

    task_list.destroy(session)

    assert TaskList.find_by(session, user_id=user.id, obj_id=task_list.id) is None
    assert Task.find_by(session, user_id=user.id, obj_id=task1.id) is not None
    assert Task.find_by(session, user_id=user.id, obj_id=task2.id) is None


def test_task_list_serializer(create_user, create_list, create_task):
    user = create_user(email="user@example.com", username="user")
    task_list = create_list(user_id=user.id, title="List title")
    _task1 = create_task(user_id=user.id, title="Task 1")
    task2 = create_task(
        user_id=user.id, list_id=task_list.id, title="Task 2", note="Note"
    )
    task3 = create_task(user_id=user.id, list_id=task_list.id, title="Task 3")

    assert task_list.model_dump() == {
        "id": task_list.id,
        "group": None,
        "title": "List title",
        "tasks": [
            {
                "id": task2.id,
                "title": "Task 2",
                "note": "Note",
                "completed": False,
                "created_at": str(task2.created_at),
                "updated_at": str(task2.updated_at),
            },
            {
                "id": task3.id,
                "title": "Task 3",
                "note": "",
                "completed": False,
                "created_at": str(task3.created_at),
                "updated_at": str(task3.updated_at),
            },
        ],
    }


def test_task_list_serializer_excluding_tasks(create_user, create_list, create_task):
    user = create_user(email="user@example.com", username="user")
    task_list = create_list(user_id=user.id, title="List title")
    create_task(user_id=user.id, title="Task 1")
    create_task(user_id=user.id, list_id=task_list.id, title="Task 2", note="Note")
    create_task(user_id=user.id, list_id=task_list.id, title="Task 3")

    assert task_list.serializer(include_tasks=False) == {
        "id": task_list.id,
        "group": None,
        "title": "List title",
    }


def test_task_list_serializer_with_group(create_user, create_list, create_group):
    user = create_user(email="user@example.com", username="user")
    group = create_group(user_id=user.id, title="Group title")
    task_list = create_list(user_id=user.id, group_id=group.id, title="List title")

    assert task_list.model_dump() == {
        "id": task_list.id,
        "group": {
            "id": group.id,
            "title": group.title,
        },
        "title": "List title",
        "tasks": [],
    }


def test_task_list_serializer_with_group_excluding_group(
    create_user, create_list, create_group
):
    user = create_user(email="user@example.com", username="user")
    group = create_group(user_id=user.id, title="Group title")
    task_list = create_list(user_id=user.id, group_id=group.id, title="List title")

    assert task_list.serializer(include_group=False) == {
        "id": task_list.id,
        "title": "List title",
        "tasks": [],
    }
