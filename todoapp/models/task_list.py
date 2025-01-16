from typing import TYPE_CHECKING, Any

from pydantic import model_serializer
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, Session, select

from todoapp.models.base_model import BaseModel
from todoapp.models.user import User

# Prevents circular imports problem
if TYPE_CHECKING:
    from todoapp.models.task import Task


class TaskList(BaseModel, table=True):
    """List allows to group several tasks"""

    __tablename__ = "list"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    title: str = Field(min_length=3, max_length=50, nullable=False)

    user: "User" = Relationship(back_populates="task_lists")
    tasks: list["Task"] = Relationship(back_populates="task_list", cascade_delete=True)

    @model_serializer
    def serializer(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "tasks": [task.serializer(include_task_list=False) for task in self.tasks],
        }

    @classmethod
    def all(cls: "TaskList", session: Session, **filters: Any) -> list["TaskList"]:
        """Fetch all records, optionally filtering by giving parameters"""
        stmt = select(cls).options(selectinload(cls.tasks))
        for attr, value in filters.items():
            stmt = stmt.where(getattr(cls, attr) == value)

        return session.exec(stmt).fetchall()
