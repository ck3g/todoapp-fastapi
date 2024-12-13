from datetime import UTC, datetime
from typing import List

from sqlmodel import Field, Session, SQLModel, select


class Task(SQLModel, table=True):
    """Represents model to describe tasks"""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=3, max_length=255, nullable=False)
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default=datetime.now(UTC), nullable=False)

    @classmethod
    def find_by(cls, session: Session, task_id: int, user_id: int) -> "Task | None":
        """Finds a task by id and user_id"""
        return session.exec(
            select(cls).where(cls.id == task_id, cls.user_id == user_id)
        ).first()

    @classmethod
    def all(cls, session: Session, user_id: int) -> "List[Task]":
        """Selects all tasks"""
        return session.exec(select(cls).where(cls.user_id == user_id))
