from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import orm

from api.database import get_session
from api.models import User
from api.repositories import (
    RepositoryConflictError,
    UserRepository,
    get_user_repository,
)
from api.schemas import (
    MessageSchema,
    PaginationFilter,
    UserPublicListSchema,
    UserPublicSchema,
    UserSchema,
    UserUpdateSchema,
)
from api.security import get_current_user

router = APIRouter(prefix='/users', tags=['users'])


Session = Annotated[orm.Session, Depends(get_session)]

CurrentUser = Annotated[User, Depends(get_current_user)]

UsersPagination = Annotated[PaginationFilter, Query()]

UserRepo = Annotated[
    UserRepository,
    Depends(get_user_repository),
]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=UserPublicListSchema
)
async def read_users(
    current_user: CurrentUser,
    user_repo: UserRepo,
    pagination: UsersPagination,
):
    users = user_repo.get_users(pagination)
    return {'users': users}


@router.get(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema
)
async def read_user(
    user_id: int, current_user: CurrentUser, user_repo: UserRepo
):
    user = user_repo.get_user_by_id(user_id)
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
async def create_user(user_data: UserSchema, user_repo: UserRepo):
    try:
        db_user = user_repo.create_user(user_data)
    except RepositoryConflictError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(e),
        )
    return db_user


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublicSchema
)
async def update_user(
    user_id: int,
    user: UserUpdateSchema,
    current_user: CurrentUser,
    user_repo: UserRepo,
):
    db_user = user_repo.get_user_by_id(user_id)
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
        updated_user = user_repo.update_user(user_id, user)
    except RepositoryConflictError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(e),
        )

    return updated_user


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
)
async def delete_user(
    user_id: int, current_user: CurrentUser, user_repo: UserRepo
):
    db_user = user_repo.get_user_by_id(user_id)
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

    user_repo.delete_user(user_id)

    return {'message': 'User deleted successfully'}
