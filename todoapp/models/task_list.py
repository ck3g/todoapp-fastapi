from datetime import UTC, datetime
from typing import Any, List

from pydantic import model_serializer
from sqlmodel import Field, Session, SQLModel, select


class TaskList(SQLModel, table=True):
    """List allows to group several tasks"""

    __tablename__ = "list"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=3, max_length=50, nullable=False)
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default=datetime.now(UTC), nullable=False)

    # @model_serializer
    # def serializer(self) -> dict[str, Any]:
    #     return {"id": self.id, "title": self.title}

    @classmethod
    def all(cls, session: Session, user_id: int | None = None) -> "List[TaskList]":
        """Select all task lists"""
        stmt = select(cls)
        if user_id is not None:
            stmt = stmt.where(cls.user_id == user_id)

        return session.exec(stmt).fetchall()

    @classmethod
    def create_by(cls, session: Session, **kwargs) -> "TaskList":
        """Creates a new task list with provided parameters"""
        lst = cls()
        for attr, value in kwargs.items():
            setattr(lst, attr, value)

        session.add(lst)
        session.commit()
        session.refresh(lst)

        return lst
