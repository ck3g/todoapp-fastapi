from sqlmodel import Session

from todoapp.models import Group, TaskList


def test_group_destroy(session: Session, create_user, create_list, create_group):
    user = create_user(email="user@example.com", username="user")
    group1 = create_group(user_id=user.id, title="Group 1 title")
    group2 = create_group(user_id=user.id, title="Group 2 title")
    task_list1 = create_list(user_id=user.id, group_id=group1.id, title="List 1")
    task_list2 = create_list(user_id=user.id, group_id=group1.id, title="List 2")
    task_list3 = create_list(
        user_id=user.id, group_id=group2.id, title="Ungrouped list"
    )

    group1.destroy(session)

    assert task_list1.group is None
    assert task_list2.group is None
    assert task_list3.group == group2


def test_group_serializer(create_user, create_list, create_group):
    user = create_user(email="user@example.com", username="user")
    group_with_lists = create_group(user_id=user.id, title="Group 1")
    group_without_lists = create_group(user_id=user.id, title="Group 2")
    task_list1 = create_list(
        user_id=user.id, group_id=group_with_lists.id, title="List 1"
    )
    task_list2 = create_list(
        user_id=user.id, group_id=group_with_lists.id, title="List 2"
    )

    assert group_with_lists.model_dump() == {
        "id": group_with_lists.id,
        "title": "Group 1",
        "task_lists": [
            {"id": task_list1.id, "title": "List 1"},
            {"id": task_list2.id, "title": "List 2"},
        ],
    }

    assert group_without_lists.model_dump() == {
        "id": group_without_lists.id,
        "title": "Group 2",
        "task_lists": [],
    }


def test_group_serializer_without_task_lists(create_user, create_list, create_group):
    user = create_user(email="user@example.com", username="user")
    group = create_group(user_id=user.id, title="Group 1")
    create_list(user_id=user.id, group_id=group.id, title="List 1")

    assert group.serializer(include_task_lists=False) == {
        "id": group.id,
        "title": "Group 1",
    }
