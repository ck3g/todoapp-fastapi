from typing import TYPE_CHECKING, Any

from pydantic import model_serializer
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, Session, select

from todoapp.models.base_model import BaseModel
from todoapp.models.group import Group
from todoapp.models.user import User

# Prevents circular imports problem
if TYPE_CHECKING:
    from todoapp.models.task import Task


class TaskList(BaseModel, table=True):
    """List allows to group several tasks"""

    __tablename__ = "list"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    group_id: int | None = Field(
        default=None, foreign_key="group.id", ondelete="SET NULL"
    )
    title: str = Field(min_length=3, max_length=50, nullable=False)

    user: "User" = Relationship(back_populates="task_lists")
    group: "Group" = Relationship(back_populates="task_lists")
    tasks: list["Task"] = Relationship(back_populates="task_list", cascade_delete=True)

    @model_serializer
    def serializer(
        self, include_tasks: bool = True, include_group: bool = True
    ) -> dict[str, Any]:
        task_list_dict = {
            "id": self.id,
            "title": self.title,
        }

        if include_tasks:
            task_list_dict["tasks"] = [
                task.serializer(include_task_list=False) for task in self.tasks
            ]

        if include_group:
            task_list_dict["group"] = (
                self.group.serializer(include_task_lists=False)
                if self.group is not None
                else None
            )

        return task_list_dict

    @classmethod
    def all(cls: "TaskList", session: Session, **filters: Any) -> list["TaskList"]:
        """Fetch all records, optionally filtering by giving parameters"""
        stmt = select(cls).options(selectinload(cls.tasks))
        for attr, value in filters.items():
            stmt = stmt.where(getattr(cls, attr) == value)

        return session.exec(stmt).fetchall()
