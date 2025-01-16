from datetime import date
from typing import Any, Optional

from pydantic import model_serializer
from sqlmodel import Field, Relationship

from todoapp.models.base_model import BaseModel
from todoapp.models.task_list import TaskList
from todoapp.models.user import User


class Task(BaseModel, table=True):
    """Represents model to describe tasks"""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    list_id: int | None = Field(
        foreign_key="list.id", nullable=True, ondelete="CASCADE"
    )
    title: str = Field(min_length=3, max_length=255, nullable=False)
    note: str = Field(max_length=1_000, default="", nullable=False)
    completed: bool = Field(nullable=False, default=False)
    due_date: date = Field(nullable=True)

    user: "User" = Relationship(back_populates="tasks")
    task_list: Optional["TaskList"] = Relationship(back_populates="tasks")

    @model_serializer
    def serializer(self, include_task_list: bool = True) -> dict[str, Any]:
        task_list = (
            {
                "id": self.task_list.id,
                "title": self.task_list.title,
            }
            if self.task_list is not None
            else None
        )

        task_dict = {
            "id": self.id,
            "title": self.title,
            "note": self.note,
            "completed": self.completed,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

        if include_task_list:
            task_dict["task_list"] = task_list

        return task_dict
