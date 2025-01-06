from datetime import UTC, date, datetime
from typing import Any, List

from pydantic import model_serializer
from sqlmodel import Field, Session, SQLModel, select


class Task(SQLModel, table=True):
    """Represents model to describe tasks"""

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=3, max_length=255, nullable=False)
    note: str = Field(max_length=1_000, default="", nullable=False)
    completed: bool = Field(nullable=False, default=False)
    due_date: date = Field(nullable=True)
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default=datetime.now(UTC), nullable=False)

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

    @classmethod
    def find_by(cls, session: Session, task_id: int, user_id: int) -> "Task | None":
        """Finds a task by id and user_id"""
        return session.exec(
            select(cls).where(cls.id == task_id, cls.user_id == user_id)
        ).first()

    @classmethod
    def all(cls, session: Session, user_id: int | None = None) -> "List[Task]":
        """Selects all tasks"""
        stmt = select(cls)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)

        return session.exec(stmt).fetchall()

    @classmethod
    def create_by(cls, session: Session, **kwargs) -> "Task":
        """Creates a new task with provided parameters"""
        task = cls()
        for attr, value in kwargs.items():
            setattr(task, attr, value)

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def update(self, session: Session, **kwargs) -> "Task":
        """Updates an existing task"""
        self.updated_at = datetime.now(UTC)

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        session.add(self)
        session.commit()
        session.refresh(self)

        return self

    def destroy(self, session: Session):
        """Deletes the task from the database"""
        session.delete(self)
        session.commit()
