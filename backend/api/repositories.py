from typing import Annotated

import sqlalchemy
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.database import Session, get_session
from api.models import User
from api.schemas import UserSchema, UserUpdateSchema
from api.security import get_password_hash


class RepositoryConflictError(Exception):
    pass


class RepositoryNotFoundError(Exception):
    pass


class UserRepository:
    def __init__(self, session: sqlalchemy.orm.Session):
        self.session = session

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.session.scalar(select(User).filter(User.id == user_id))

    def get_user_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).filter(User.username == username)
        )

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).filter(User.email == email))

    def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.session.scalars(
            select(User).offset(skip).limit(limit)
        ).all()

    def create_user(self, user_data: UserSchema) -> User:
        db_user = User(
            **user_data.model_dump()
            | {'password': get_password_hash(user_data.password)}
        )

        self.session.add(db_user)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()

            if 'username' in str(e.orig):
                raise RepositoryConflictError('Username already exists.')
            if 'email' in str(e.orig):
                raise RepositoryConflictError('Email already exists.')

        else:
            self.session.refresh(db_user)

        return db_user

    def update_user(self, user_id: int, user_data: UserUpdateSchema) -> User:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise RepositoryNotFoundError('User not found.')

        for key, value in user_data.model_dump(exclude_unset=True).items():
            if key == 'password':
                new_password = get_password_hash(value)
                setattr(db_user, key, new_password)
            else:
                setattr(db_user, key, value)

        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()

            if 'username' in str(e.orig):
                raise RepositoryConflictError('Username already exists.')
            if 'email' in str(e.orig):
                raise RepositoryConflictError('Email already exists.')

        else:
            self.session.refresh(db_user)

        return db_user

    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise RepositoryNotFoundError('User not found.')

        self.session.delete(db_user)
        self.session.commit()


def get_user_repository(
    session: Annotated[Session, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)
