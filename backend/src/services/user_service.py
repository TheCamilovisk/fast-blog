from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import CreateUserRequest
from src.utils.security import hash_password, verify_password


class UserService:
    @staticmethod
    async def create_user(
        session: AsyncSession, user_data: CreateUserRequest
    ) -> User:
        if await UserRepository.get_by_email(session, user_data.email):
            raise ValueError('Email already registered')

        hashed_pwd = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_pwd,
        )

        return await UserRepository.create(session, user)

    @staticmethod
    async def get_by_username_or_email(
        session: AsyncSession, identifier: str
    ) -> User | None:
        return await UserRepository.get_by_username_or_email(
            session, identifier
        )

    @staticmethod
    async def authenticate(
        session: AsyncSession, identifier: str, password: str
    ) -> User | None:
        user = await UserRepository.get_by_username_or_email(
            session, identifier
        )
        if user and verify_password(password, user.password):
            return user
        return None
