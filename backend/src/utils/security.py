from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict
from zoneinfo import ZoneInfo

import jwt
from jose import JWTError
from passlib.context import CryptContext

from src.core.settings import get_settings

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


class JWTTokenType(Enum):
    ACCESS: str = 'access'
    REFRESH: str = 'refresh'


settings = get_settings()


def hash_password(password: str) -> str:
    """
    Hashes the plain-text password using Argon2.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """
    Verifies a plain-text password agains the stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(tz=ZoneInfo('UTC')) + delta
    to_encode.update({'exp': expire, 'type': JWTTokenType.ACCESS.value})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(data: Dict[str, Any]):
    to_encode = data.copy()
    delta = timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(ZoneInfo('UTC')) + delta
    to_encode.update({'exp': expire, 'type': JWTTokenType.REFRESH.value})
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str, token_type: str) -> Dict[str, Any]:
    """
    Decode & validate a JWT, ensuring it's of the expectged `token_type`
    (either "access" or "refresh")
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        raise
    if payload.get('type') != token_type:
        raise JWTError(f'Invalid token type: expected {token_type}')
    return payload
