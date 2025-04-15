from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import orm
from sqlalchemy.exc import IntegrityError

from api.database import get_session
from api.models.user import User
from api.repositories.user_repository import UserRepository
from api.schemas import (
    MessageSchema,
    UserPublicSchema,
    UserSchema,
    UserSearchSchema,
    UsersSearchResultSchema,
    UserUpdateSchema,
)
from api.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])


DBSession = Annotated[orm.Session, Depends(get_session)]

CurrentUser = Annotated[User, Depends(get_current_user)]

SearchParams = Annotated[UserSearchSchema, Query()]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=UsersSearchResultSchema
)
async def read_users(
    current_user: CurrentUser,
    session: DBSession,
    pagination: SearchParams,
):
    users = UserRepository.list_all(
        session,
        username=pagination.username,
        email=pagination.email,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return {
        'search_params': pagination,
        'total_items': len(users),
        'users': users,
    }


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema
)
async def read_user(
    user_id: int,
    session: DBSession,
    current_user: CurrentUser,
):
    user = UserRepository.get_by_id(session, user_id)
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
async def create_user(user_data: UserSchema, session: DBSession):
    try:
        db_user = UserRepository.create(
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
    session: DBSession,
):
    db_user = UserRepository.get_by_id(session, user_id)
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
        db_user = UserRepository.update(
            session,
            obj=db_user,
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
    session: DBSession,
):
    db_user = UserRepository.get_by_id(session, user_id)
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

    UserRepository.delete(session, db_user)

    return {'message': 'User deleted successfully'}
