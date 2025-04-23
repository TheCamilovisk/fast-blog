from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.repositories.user_repository import UserRepository
from api.schemas import TokenSchema
from api.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', status_code=HTTPStatus.OK, response_model=TokenSchema)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
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

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }
