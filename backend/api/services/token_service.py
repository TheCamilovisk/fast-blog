from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.token import RefreshToken


class RefreshTokenService:
    @classmethod
    async def create(
        cls, session: AsyncSession, refresh_token: str, user_id: int
    ) -> RefreshToken:
        token = RefreshToken(refresh_token, user_id)

        session.add(token)

        await session.commit()
        await session.refresh(token)
        return token

    @classmethod
    async def delete(cls, session: AsyncSession, token: RefreshToken):
        await session.delete(token)
        await session.commit()

    @classmethod
    async def find(
        cls, session: AsyncSession, refresh_token: str
    ) -> RefreshToken | None:
        return await session.scalar(
            select(RefreshToken).filter(RefreshToken.token == refresh_token)
        )
