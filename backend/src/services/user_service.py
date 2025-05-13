from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import CreateUserRequest
from src.utils.security import hash_password


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
