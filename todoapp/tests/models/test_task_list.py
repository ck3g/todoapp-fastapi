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
