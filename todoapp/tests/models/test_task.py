def test_task_serializer_without_task_list(create_task, create_user):
    user = create_user(email="user@example.com", username="user")
    task = create_task(user_id=user.id, title="Task title", note="Task note")

    assert task.model_dump() == {
        "id": task.id,
        "task_list": None,
        "title": "Task title",
        "note": "Task note",
        "completed": False,
        "created_at": str(task.created_at),
        "updated_at": str(task.updated_at),
    }


def test_task_serializer_excluding_task_list(create_task, create_user):
    user = create_user(email="user@example.com", username="user")
    task = create_task(user_id=user.id, title="Task title", note="Task note")

    assert task.serializer(include_task_list=False) == {
        "id": task.id,
        "title": "Task title",
        "note": "Task note",
        "completed": False,
        "created_at": str(task.created_at),
        "updated_at": str(task.updated_at),
    }


def test_task_serializer_with_task_list(create_task, create_user, create_list):
    user = create_user(email="user@example.com", username="user")
    task_list = create_list(user_id=user.id, title="List title")
    task = create_task(
        user_id=user.id, list_id=task_list.id, title="Task title", note="Task note"
    )

    assert task.model_dump() == {
        "id": task.id,
        "task_list": {
            "id": task_list.id,
            "title": task_list.title,
        },
        "title": "Task title",
        "note": "Task note",
        "completed": False,
        "created_at": str(task.created_at),
        "updated_at": str(task.updated_at),
    }
