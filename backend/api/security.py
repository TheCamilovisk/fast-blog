from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models.user import User
from api.settings import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

PWD_CONTEXT = PasswordHash.recommended()


class CredentialsException(RuntimeError):
    pass


OAuth2Scheme = Annotated[
    str,
    Depends(
        OAuth2PasswordBearer(
            tokenUrl='/auth/token',
            scheme_name='JWT',
            description='JWT authentication scheme',
        )
    ),
]


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(tz=ZoneInfo('UTC')) + expire_delta
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire_delta.total_seconds()


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(tz=ZoneInfo('UTC')) + expire_delta
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire_delta.total_seconds()


def get_password_hash(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_refresh_token_sub(token: str) -> str:
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        now = datetime.now(tz=ZoneInfo('UTC'))
        if (
            datetime.fromtimestamp(payload.get('exp'), tz=ZoneInfo('UTC'))
            < now
        ):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Refresh token expired',
            )
    except DecodeError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Could not validate credentials',
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Refresh token has expired',
        )

    return payload.get('sub')


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token: OAuth2Scheme,
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
    )

    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        now = datetime.now(ZoneInfo('UTC'))
        if datetime.fromtimestamp(payload.get('exp')) < now:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Refresh token expired',
            )

        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Token has expired',
        )

    user = await session.scalar(
        select(User).filter(User.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user
