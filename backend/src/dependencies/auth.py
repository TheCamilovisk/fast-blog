from http import HTTPStatus
from typing import Annotated

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.models.user import User
from src.services.user_service import UserService
from src.utils.security import JWTTokenType, decode_token

OAuth2Scheme = Annotated[str, OAuth2PasswordBearer(tokenUrl='/auth/token')]
DBSession = Annotated[AsyncSession, get_session]


async def get_current_user(token: OAuth2Scheme, session: DBSession) -> User:
    invalid_credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
    )
    try:
        payload = decode_token(token, token_type=JWTTokenType.ACCESS.value)
        username = payload.get('sub')
    except Exception:
        raise invalid_credentials_exception
    if not username:
        raise invalid_credentials_exception
    user = await UserService.get_by_username_or_email(session, username)
    if not user:
        invalid_credentials_exception
    return user
