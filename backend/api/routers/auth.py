from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.repositories.user_repository import UserRepository
from api.schemas import LoginSchema, MessageSchema, TokenSchema
from api.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_sub,
    verify_password,
)
from api.services.token_service import RefreshTokenService

router = APIRouter(prefix='/auth', tags=['auth'])


DBSession = Annotated[AsyncSession, Depends(get_session)]
RToken = Annotated[str, Body(embed=True)]


@router.post('/token', status_code=HTTPStatus.OK, response_model=LoginSchema)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: DBSession,
):
    user = await UserRepository.find_by_id_or_email(
        session,
        form_data.username,
    )

    if not (user and verify_password(form_data.password, user.password)):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(
        data={'sub': user.email},
    )
    refresh_token = create_refresh_token(data={'sub': user.email})

    await RefreshTokenService.create(session, refresh_token, user.id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
    }


@router.post('/refresh', status_code=HTTPStatus.OK, response_model=TokenSchema)
async def refresh_token(refresh_token: RToken, session: DBSession) -> dict:
    stored = await RefreshTokenService.find(session, refresh_token)
    if not stored:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid refresh token'
        )

    identifier = get_refresh_token_sub(refresh_token)
    user = await UserRepository.find_by_id_or_email(session, identifier)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid refresh token'
        )

    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post(
    '/logout', status_code=HTTPStatus.OK, response_model=MessageSchema
)
async def logout(refresh_token: RToken, session: DBSession):
    db_token = await RefreshTokenService.find(session, refresh_token)

    if db_token:
        await RefreshTokenService.delete(session, db_token)

    return {'message': 'User logged out'}
