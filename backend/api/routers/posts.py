from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.database import get_session
from api.models.profile import Profile
from api.models.user import User
from api.repositories.post_repository import PostRespository
from api.repositories.profile_repository import ProfileRepository
from api.repositories.tag_repository import TagRepository
from api.schemas import (
    MessageSchema,
    PostCreateSchema,
    PostPublicSchema,
    PostSearchResultSchema,
    PostSearchSchema,
    PostUpdateSchema,
    TagCreateSchema,
)
from api.security import get_current_user

router = APIRouter(prefix='/posts', tags=['posts'])


def get_current_user_profile(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Profile:
    profile = ProfileRepository.get_by_user_id(session, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Current user does not have a profile',
        )

    return profile


def get_tags(tags_str: str) -> list[str]:
    tags = [tag.strip() for tag in tags_str.split(',')]
    return tags


DBSession = Annotated[Session, Depends(get_session)]

CurrentAuthor = Annotated[Profile, Depends(get_current_user_profile)]

PostsFilter = Annotated[PostSearchSchema, Query()]


@router.post(
    '/', status_code=HTTPStatus.CREATED, response_model=PostPublicSchema
)
async def create_post(
    session: DBSession,
    current_author: CurrentAuthor,
    post_data: PostCreateSchema,
):
    try:
        post = PostRespository.create(
            session,
            title=post_data.title,
            subtitle=post_data.subtitle,
            content=post_data.content,
            author_id=current_author.id,
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(e.orig.args[0]),
        )
    return {
        'id': post.id,
        'title': post.title,
        'subtitle': post.subtitle,
        'slug': post.slug,
        'content': post.content,
        'is_published': post.is_published,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'published_at': post.published_at,
        'author_username': post.author.user.username,
        'tags': post.tags,
    }


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=PostSearchResultSchema
)
async def get_posts(
    session: DBSession,
    posts_filter: PostsFilter,
):
    posts = PostRespository.list_all(
        session,
        title=posts_filter.title,
        tags=posts_filter.tags,
        author_username=posts_filter.author_username,
        published_only=posts_filter.is_published,
        published_at=posts_filter.published_at,
        limit=posts_filter.limit,
        offset=posts_filter.offset,
    )
    if not posts:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='No posts found',
        )

    total_items = len(posts)

    posts = [
        {
            'id': post.id,
            'title': post.title,
            'subtitle': post.subtitle,
            'is_published': post.is_published,
            'created_at': post.created_at,
            'author_username': post.author.user.username,
            'post_url': router.url_path_for('get_post', post_id=post.id),
        }
        for post in posts
    ]

    return {
        'total_items': total_items,
        'posts': posts,
        **posts_filter.model_dump(),
    }


@router.get(
    '/{post_id}', status_code=HTTPStatus.OK, response_model=PostPublicSchema
)
async def get_post(post_id: int, session: DBSession):
    post = PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    return {
        'id': post.id,
        'title': post.title,
        'subtitle': post.subtitle,
        'slug': post.slug,
        'content': post.content,
        'is_published': post.is_published,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'published_at': post.published_at,
        'author_username': post.author.user.username,
        'tags': post.tags,
    }


@router.put(
    '/{post_id}', status_code=HTTPStatus.OK, response_model=PostPublicSchema
)
async def update_post(
    post_id: int,
    post_data: PostUpdateSchema,
    session: DBSession,
    current_author: CurrentAuthor,
):
    post = PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    if post.author_id != current_author.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to update this post',
        )

    post = PostRespository.update(
        session,
        obj=post,
        title=post_data.title,
        subtitle=post_data.subtitle,
        content=post_data.content,
    )

    return {
        'id': post.id,
        'title': post.title,
        'subtitle': post.subtitle,
        'slug': post.slug,
        'content': post.content,
        'is_published': post.is_published,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'published_at': post.published_at,
        'author_username': post.author.user.username,
        'tags': post.tags,
    }


@router.delete(
    '/{post_id}', status_code=HTTPStatus.OK, response_model=MessageSchema
)
async def delete_post(
    post_id: int, session: DBSession, current_author: CurrentAuthor
):
    post = PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    if post.author_id != current_author.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to delete this post',
        )

    PostRespository.delete(session, obj=post)
    return {'message': 'Post deleted'}


@router.post(
    '/{post_id}/publish',
    status_code=HTTPStatus.OK,
    response_model=PostPublicSchema,
)
async def publish_post(
    post_id: int,
    session: DBSession,
    current_author: CurrentAuthor,
):
    post = PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    if post.author_id != current_author.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to publish this post',
        )

    publish_date = datetime.now()

    post = PostRespository.update(
        session,
        obj=post,
        is_published=True,
        published_at=publish_date,
    )
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Failed to publish post',
        )

    return {
        'id': post.id,
        'title': post.title,
        'subtitle': post.subtitle,
        'slug': post.slug,
        'content': post.content,
        'is_published': post.is_published,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'published_at': post.published_at,
        'author_username': post.author.user.username,
        'tags': post.tags,
    }


@router.post(
    '/{post_id}/unpublish',
    status_code=HTTPStatus.OK,
    response_model=MessageSchema,
)
async def unpublish_post(
    post_id: int,
    session: DBSession,
    current_author: CurrentAuthor,
):
    post = PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    if post.author_id != current_author.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to unpublish this post',
        )

    post = PostRespository.update(
        session,
        obj=post,
        is_published=False,
        published_at=None,
    )
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Failed to unpublish post',
        )

    return {'message': 'Post unpublished'}


@router.post(
    '/{post_id}/tags',
    status_code=HTTPStatus.OK,
    response_model=PostPublicSchema,
)
async def add_tags_to_post(
    post_id: int,
    tags: TagCreateSchema,
    session: DBSession,
    current_author: CurrentAuthor,
):
    post = PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    if post.author_id != current_author.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You do not have permission to add tags to this post',
        )

    extracted_tags = TagRepository.find_or_create_multiple(
        session, tags=get_tags(tags.tags)
    )
    PostRespository.add_tags(session, post, extracted_tags)

    return {
        'id': post.id,
        'title': post.title,
        'subtitle': post.subtitle,
        'slug': post.slug,
        'content': post.content,
        'is_published': post.is_published,
        'created_at': post.created_at,
        'updated_at': post.updated_at,
        'published_at': post.published_at,
        'author_username': post.author.user.username,
        'tags': post.tags,
    }
