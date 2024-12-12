from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    title: str = Field(min_length=3, max_length=255, nullable=False)
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default=datetime.now(UTC), nullable=False)
