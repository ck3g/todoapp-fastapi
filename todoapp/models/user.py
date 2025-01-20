from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, Session, SQLModel, func, or_, select

from todoapp.security.password import hash_password

if TYPE_CHECKING:
    from todoapp.models.group import Group
    from todoapp.models.task import Task
    from todoapp.models.task_list import TaskList


class User(SQLModel, table=True):
    """Represents a model to describe a user"""

    id: int = Field(default=None, primary_key=True)
    email: str = Field(
        index=True, min_length=3, max_length=255, unique=True, nullable=False
    )
    username: str = Field(
        index=True, min_length=3, max_length=255, unique=True, nullable=False
    )
    hashed_password: str = Field(min_length=3, max_length=255, nullable=False)
    created_at: datetime = Field(default=datetime.now(UTC), nullable=False)

    groups: list["Group"] = Relationship(back_populates="user")
    tasks: list["Task"] = Relationship(back_populates="user", cascade_delete=True)
    task_lists: list["TaskList"] = Relationship(
        back_populates="user", cascade_delete=True
    )

    @classmethod
    def find_by_email(cls, session: Session, email: str) -> "User | None":
        """Finds a user by email"""
        return session.exec(
            select(cls).where(func.lower(cls.email) == func.lower(email))
        ).first()

    @classmethod
    def find_by_username(cls, session: Session, username: str) -> "User | None":
        """Finds a user by username"""
        return session.exec(
            select(cls).where(func.lower(cls.username) == func.lower(username))
        ).first()

    @classmethod
    def find_by_email_or_username(
        cls, session: Session, email_or_username: str
    ) -> "User | None":
        """Finds a user by email or username"""
        return session.exec(
            select(cls).where(
                or_(
                    func.lower(cls.email) == func.lower(email_or_username),
                    func.lower(cls.username) == func.lower(email_or_username),
                )
            )
        ).first()

    @classmethod
    def create_by(
        cls, session: Session, email: str, username: str, password: str
    ) -> "User":
        """Creates a new user"""
        hashed_password = hash_password(password)
        user = cls(email=email, username=username, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)

        return user

    def destroy(self, session: Session) -> None:
        """Delete the current record"""
        session.delete(self)
        session.commit()
