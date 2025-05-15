from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import CreateUserRequestSchema


class UserService:
    @staticmethod
    async def create_user(
        session: AsyncSession, user_data: CreateUserRequestSchema
    ) -> User:
        if await UserRepository.get_by_email(session, user_data.email):
            raise ValueError('Email already registered')

        return await UserRepository.create(
            session=session,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
        )

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
        if user and user.verify_password(password):
            return user
        return None
