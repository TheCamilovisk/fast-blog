from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import orm
from sqlalchemy.exc import IntegrityError

from api.database import get_session
from api.models.user import User
from api.schemas import (
    MessageSchema,
    PaginationFilter,
    UserPublicListSchema,
    UserPublicSchema,
    UserSchema,
    UserUpdateSchema,
)
from api.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])


Session = Annotated[orm.Session, Depends(get_session)]

CurrentUser = Annotated[User, Depends(get_current_user)]

UsersPagination = Annotated[PaginationFilter, Query()]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=UserPublicListSchema
)
async def read_users(
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
    pagination: UsersPagination,
):
    users = User.list(
        session,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return {'users': users}


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema
)
async def read_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    user = User.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if user.id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this user',
        )

    return user


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema
)
async def create_user(
    user_data: UserSchema, session: Annotated[Session, Depends(get_session)]
):
    try:
        db_user = User.create(
            session,
            username=user_data.username,
            password=get_password_hash(user_data.password),
            email=user_data.email,
        )
    except IntegrityError as e:
        session.rollback()

        if 'username' in str(e.orig):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists.',
            )
        if 'email' in str(e.orig):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists.',
            )

    return db_user


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema
)
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    db_user = User.get_by_id(session, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if current_user.id != db_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this user',
        )

    try:
        db_user = User.update(
            session,
            user=db_user,
            username=user_data.username,
            email=user_data.email,
        )
    except IntegrityError as e:
        session.rollback()

        if 'username' in str(e.orig):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists.',
            )
        if 'email' in str(e.orig):
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already exists.',
            )

    return db_user


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[Session, Depends(get_session)],
):
    db_user = User.get_by_id(session, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    if current_user.id != db_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this user',
        )

    User.delete(session, db_user)

    return {'message': 'User deleted successfully'}
