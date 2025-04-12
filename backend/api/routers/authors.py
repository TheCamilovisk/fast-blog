from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_session
from api.models.user import User
from api.repositories.profile_repository import ProfileRepository
from api.schemas import (
    AuthorCreateSchema,
    AuthorPublicSchema,
    AuthorsSearchResultSchema,
    AuthorsSearchSchema,
    AuthorUpdateSchema,
    MessageSchema,
)
from api.security import get_current_user

router = APIRouter(prefix='/authors', tags=['authors'])

DBSession = Annotated[Session, Depends(get_session)]

AuthorsQuery = Annotated[AuthorsSearchSchema, Query()]

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=AuthorsSearchResultSchema
)
def read_authors(session: DBSession, query_params: AuthorsQuery):
    profiles = ProfileRepository.list(
        session,
        username=query_params.username,
        firstname=query_params.firstname,
        lastname=query_params.lastname,
        limit=query_params.limit,
        offset=query_params.offset,
    )

    authors = [
        {
            'id': profile.id,
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
        'total_items': len(authors),
        'authors': authors,
    }


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=AuthorPublicSchema,
)
def read_author(
    session: DBSession,
    user_id: int,
    current_user: CurrentUser,
):
    profile = ProfileRepository.get_by_id(session, user_id)
    if not profile:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )

    if profile.user.id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to access this author',
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
def crete_author(
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
        profile = ProfileRepository.create(
            session,
            firstname=author_data.firstname,
            lastname=author_data.lastname,
            bio=author_data.bio,
            website=author_data.website,
            user_id=user_id,
        )
    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Profile already exists.',
        )

    author = {
        'id': profile.id,
        'username': profile.user.username,
        'firstname': profile.firstname,
        'lastname': profile.lastname,
        'email': profile.user.email,
        'bio': profile.bio,
        'website': profile.website,
    }

    return author


@router.put(
    '/{author_id}',
    status_code=HTTPStatus.OK,
    response_model=AuthorPublicSchema,
)
def update_author(
    session: DBSession,
    author_id: int,
    author_data: AuthorUpdateSchema,
    current_user: CurrentUser,
):
    db_profile = ProfileRepository.get_by_id(session, author_id)
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
        db_profile = ProfileRepository.update(
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
        'username': db_profile.user.username,
        'firstname': db_profile.firstname,
        'lastname': db_profile.lastname,
        'email': db_profile.user.email,
        'bio': db_profile.bio,
        'website': db_profile.website,
    }


@router.delete(
    '/{profile_id}',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
)
def delete_author(
    session: DBSession,
    profile_id: int,
    current_user: CurrentUser,
):
    db_profile = ProfileRepository.get_by_id(session, profile_id)
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

    ProfileRepository.delete(session, db_profile)

    return {
        'message': 'Author deleted successfully',
    }
