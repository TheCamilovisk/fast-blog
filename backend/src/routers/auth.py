from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.core.dependencies import DBSession
from src.schemas.token import RefreshTokenRequestSchema, TokenSchema
from src.services.user_service import UserService
from src.utils.security import (
    JWTTokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', status_code=HTTPStatus.CREATED)
async def login(form_data: OAuth2Form, session: DBSession) -> TokenSchema:
    user = await UserService.authenticate(
        session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )
    payload = {'sub': user.username}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
    }


@router.post('/refresh', status_code=HTTPStatus.CREATED)
async def refresh_access_token(
    body: RefreshTokenRequestSchema, session: DBSession
) -> TokenSchema:
    try:
        payload = decode_token(
            body.refresh_token, token_type=JWTTokenType.REFRESH.value
        )
        username = payload.get('sub')
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid refresh token'
        )
    user = await UserService.get_by_username_or_email(session, username)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid refresh token'
        )
    payload = {'sub': user.username}
    new_access_token = create_access_token(payload)
    new_refresh_token = create_refresh_token(payload)
    return {
        'access_token': new_access_token,
        'refresh_token': new_refresh_token,
        'token_type': 'bearer',
    }
