from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class UserRepository:
    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> User | None:
        "Return the User with this email, or None if not found."
        result = await session.scalar(select(User).filter_by(email=email))
        return result

    @staticmethod
    async def get_by_username_or_email(
        session: AsyncSession, identifier: str
    ) -> User | None:
        """
        Fetches a user by username or email.
        """
        query = select(User).filter(
            or_(User.username == identifier, User.email == identifier)
        )
        result = await session.scalars(query)
        return result.first()

    @staticmethod
    async def create(session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
