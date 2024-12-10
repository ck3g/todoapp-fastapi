from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel, func, or_, select

from todoapp.security.password import hash_password


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

    @classmethod
    def find_by_email(self, session: Session, email: str) -> "User | None":
        return session.exec(
            select(User).where(func.lower(User.email) == func.lower(email))
        ).first()

    @classmethod
    def find_by_username(self, session: Session, username: str) -> "User | None":
        return session.exec(
            select(User).where(func.lower(User.username) == func.lower(username))
        ).first()

    @classmethod
    def find_by_email_or_username(
        self, session: Session, email_or_username: str
    ) -> "User | None":
        return session.exec(
            select(User).where(
                or_(
                    func.lower(User.email) == func.lower(email_or_username),
                    func.lower(User.username) == func.lower(email_or_username),
                )
            )
        ).first()

    @classmethod
    def create_by(
        self, session: Session, email: str, username: str, password: str
    ) -> "User":
        hashed_password = hash_password(password)
        user = User(email=email, username=username, hashed_password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)

        return user
