from datetime import datetime, UTC
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(
        index=True, min_length=3, max_length=255, unique=True, nullable=False
    )
    username: str = Field(
        index=True, min_length=3, max_length=255, unique=True, nullable=False
    )
    hashed_password: str = Field(min_length=3, max_length=255, nullable=False)
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)
