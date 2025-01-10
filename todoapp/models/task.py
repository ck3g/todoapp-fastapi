from datetime import UTC, date, datetime
from typing import Any

from pydantic import model_serializer
from sqlmodel import Field

from todoapp.models.base_model import BaseModel


class Task(BaseModel, table=True):
    """Represents model to describe tasks"""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    list_id: int = Field(foreign_key="list.id", nullable=True)
    title: str = Field(min_length=3, max_length=255, nullable=False)
    note: str = Field(max_length=1_000, default="", nullable=False)
    completed: bool = Field(nullable=False, default=False)
    due_date: date = Field(nullable=True)

    @model_serializer
    def serializer(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "note": self.note,
            "completed": self.completed,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
