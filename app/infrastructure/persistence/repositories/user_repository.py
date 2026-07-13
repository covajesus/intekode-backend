"""User repository — SQLAlchemy implementation."""

from sqlalchemy.orm import Session

from app.domain.interfaces.repositories import IUserRepository
from app.infrastructure.persistence.models.user import User


class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_username(self, username: str) -> User | None:
        return self._session.query(User).filter(User.username == username).first()

    def find_by_username_or_email(self, username: str, email: str) -> User | None:
        return (
            self._session.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )

    def create(self, user: User) -> User:
        self._session.add(user)
        return user

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, entity: User) -> User:
        self._session.refresh(entity)
        return entity
