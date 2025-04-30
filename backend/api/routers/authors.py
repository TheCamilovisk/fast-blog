from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.schemas import (
    AuthorCreateSchema,
    AuthorPublicSchema,
    AuthorsSearchResultSchema,
    AuthorsSearchSchema,
    AuthorUpdateSchema,
    MessageSchema,
)
from api.core.security import get_current_user
from api.models.user import User
from api.repositories.profile_repository import ProfileRepository

router = APIRouter(prefix='/authors', tags=['authors'])

DBSession = Annotated[AsyncSession, Depends(get_session)]

AuthorsQuery = Annotated[AuthorsSearchSchema, Query()]

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=AuthorsSearchResultSchema
)
async def read_authors(session: DBSession, query_params: AuthorsQuery):
    total, profiles = await ProfileRepository.list_all(
        session,
        username=query_params.username,
        firstname=query_params.firstname,
        lastname=query_params.lastname,
        limit=query_params.limit,
        offset=query_params.offset,
    )

    authors = [
        {
            'id': profile.user.id,
            'username': profile.user.username,
            'firstname': profile.firstname,
            'lastname': profile.lastname,
            'author_url': router.url_path_for(
                'read_author', user_id=profile.user.id
            ),
        }
        for profile in profiles
    ]

    return {
        'search_params': query_params,
        'total_items': total,
        'authors': authors,
    }


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=AuthorPublicSchema,
)
async def read_author(
    session: DBSession,
    user_id: int,
):
    profile = await ProfileRepository.get_by_user_id(session, user_id)
    if not profile:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )

    author = {
        'id': profile.id,
        'user_id': profile.user.id,
        'username': profile.user.username,
        'firstname': profile.firstname,
        'lastname': profile.lastname,
        'email': profile.user.email,
        'bio': profile.bio,
        'website': profile.website,
    }

    return author


@router.post(
    '/{user_id}',
    status_code=HTTPStatus.CREATED,
    response_model=AuthorPublicSchema,
)
async def crete_author(
    session: DBSession,
    user_id: int,
    author_data: AuthorCreateSchema,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this user',
        )

    try:
        profile = await ProfileRepository.create(
            session,
            firstname=author_data.firstname,
            lastname=author_data.lastname,
            bio=author_data.bio,
            website=author_data.website,
            user_id=user_id,
        )
    except IntegrityError:
        await session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Profile already exists.',
        )

    author = {
        'id': profile.id,
        'user_id': profile.user.id,
        'username': profile.user.username,
        'firstname': profile.firstname,
        'lastname': profile.lastname,
        'email': profile.user.email,
        'bio': profile.bio,
        'website': profile.website,
    }

    return author


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=AuthorPublicSchema,
)
async def update_author(
    session: DBSession,
    user_id: int,
    author_data: AuthorUpdateSchema,
    current_user: CurrentUser,
):
    db_profile = await ProfileRepository.get_by_user_id(session, user_id)
    if not db_profile:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )

    if current_user.id != db_profile.user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this author profile',
        )

    try:
        db_profile = await ProfileRepository.update(
            session,
            obj=db_profile,
            firstname=author_data.firstname,
            lastname=author_data.lastname,
            bio=author_data.bio,
            website=author_data.website,
        )
    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Profile already exists.',
        )

    return {
        'id': db_profile.id,
        'user_id': db_profile.user.id,
        'username': db_profile.user.username,
        'firstname': db_profile.firstname,
        'lastname': db_profile.lastname,
        'email': db_profile.user.email,
        'bio': db_profile.bio,
        'website': db_profile.website,
    }


@router.delete(
    '/{author_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
)
async def delete_author(
    session: DBSession,
    author_id: int,
    current_user: CurrentUser,
):
    db_profile = await ProfileRepository.get_by_id(session, author_id)
    if not db_profile:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )

    if current_user.id != db_profile.user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this author profile',
        )

    await ProfileRepository.delete(session, db_profile)

    return {
        'message': 'Author deleted successfully',
    }
