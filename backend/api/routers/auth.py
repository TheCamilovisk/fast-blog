from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.repositories import UserRepository, get_user_repository
from api.schemas import TokenSchema
from api.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', status_code=HTTPStatus.OK, response_model=TokenSchema)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
):
    user = user_repo.get_user_by_email(form_data.username)

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
