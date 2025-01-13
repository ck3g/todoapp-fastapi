from sqlmodel import Session

from todoapp.models import Task, TaskList, User


def test_user_destroy(session: Session, create_user, create_list, create_task):
    user = create_user(email="user@example.com", username="user")
    task_list = create_list(user_id=user.id, title="List title")
    create_task(user_id=user.id, title="Task 1")
    create_task(user_id=user.id, list_id=task_list.id, title="Task 2")

    user.destroy(session)

    assert User.find_by_email(session, email=user.email) is None
    assert len(TaskList.all(session, user_id=user.id)) == 0
    assert len(Task.all(session, user_id=user.id)) == 0
