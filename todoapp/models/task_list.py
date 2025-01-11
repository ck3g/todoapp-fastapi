from typing import TYPE_CHECKING, Any

from pydantic import model_serializer
from sqlmodel import Field, Relationship

from todoapp.models.base_model import BaseModel

# Prevents circular imports problem
if TYPE_CHECKING:
    from todoapp.models.task import Task


class TaskList(BaseModel, table=True):
    """List allows to group several tasks"""

    __tablename__ = "list"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=3, max_length=50, nullable=False)

    tasks: list["Task"] = Relationship(back_populates="task_list")

    @model_serializer
    def serializer(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title}
