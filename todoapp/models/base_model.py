from datetime import UTC, datetime
from typing import Any, List, Optional, Type, TypeVar

from sqlmodel import Field, Session, SQLModel, select

T = TypeVar("T", bound="BaseModel")


class BaseModel(SQLModel):
    """Base model providing common methods"""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )

    @classmethod
    def find_by(cls, session: Session, obj_id: int, user_id: int) -> Optional[T]:
        """Find a record by its ID and user_id"""
        return session.exec(
            select(cls).where(cls.id == obj_id, cls.user_id == user_id)
        ).first()

    @classmethod
    def all(cls: Type[T], session: Session, **filters: Any) -> List[T]:
        """Fetch all records, optionally filtering by giving parameters"""
        stmt = select(cls)
        for attr, value in filters.items():
            stmt = stmt.where(getattr(cls, attr) == value)

        return session.exec(stmt).fetchall()

    @classmethod
    def create_by(cls: Type[T], session: Session, **kwargs: Any) -> T:
        """Create a new record"""
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)

        return obj

    def update(self: T, session: Session, **kwargs: Any) -> T:
        """Update the current record"""
        self.updated_at = datetime.now(UTC)

        for attr, value in kwargs.items():
            setattr(self, attr, value)

        session.add(self)
        session.commit()
        session.refresh(self)

        return self

    def destroy(self: T, session: Session) -> None:
        """Delete the current record"""
        session.delete(self)
        session.commit()
