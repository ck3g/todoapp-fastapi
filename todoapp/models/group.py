from typing import TYPE_CHECKING, Any

from pydantic import model_serializer
from sqlmodel import Field, Relationship

from todoapp.models.base_model import BaseModel
from todoapp.models.user import User

if TYPE_CHECKING:
    from todoapp.models.task_list import TaskList


class Group(BaseModel, table=True):
    """Group is a collection of task lists"""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    title: str = Field(min_length=3, max_length=50, nullable=False)

    user: "User" = Relationship(back_populates="groups")
    task_lists: list["TaskList"] = Relationship(back_populates="group")

    @model_serializer
    def serializer(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "task_lists": [
                tl.serializer(include_tasks=False) for tl in self.task_lists
            ],
        }
