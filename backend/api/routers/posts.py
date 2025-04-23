from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_session
from api.models.post import Post
from api.models.profile import Profile
from api.models.user import User
from api.repositories.post_repository import PostRespository
from api.repositories.profile_repository import ProfileRepository
from api.repositories.tag_repository import TagRepository
from api.schemas import (
    AuthorListSchema,
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


async def get_current_user_profile(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Profile:
    profile = await ProfileRepository.get_by_user_id(session, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Current user does not have a profile',
        )

    return profile


def parser_author(author: Profile) -> AuthorListSchema:
    return AuthorListSchema(
        id=author.user_id,
        username=author.user.username,
        firstname=author.firstname,
        lastname=author.lastname,
    )


def parse_post(post: Post) -> PostPublicSchema:
    return PostPublicSchema(
        id=post.id,
        title=post.title,
        subtitle=post.subtitle,
        slug=post.slug,
        content=post.content,
        is_published=post.is_published,
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at,
        author=parser_author(post.author),
        tags=[tag.name for tag in post.tags],
    )


DBSession = Annotated[AsyncSession, Depends(get_session)]

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
        post = await PostRespository.create(
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

    return parse_post(post)


@router.get(
    '/', status_code=HTTPStatus.OK, response_model=PostSearchResultSchema
)
async def get_posts(
    session: DBSession,
    posts_filter: PostsFilter,
):
    tags = (
        [tag.strip() for tag in posts_filter.tags.split(',')]
        if posts_filter.tags
        else []
    )
    (total_items, posts) = await PostRespository.list_all(
        session,
        title=posts_filter.title,
        tags=tags,
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

    posts = [
        {
            'id': post.id,
            'title': post.title,
            'subtitle': post.subtitle,
            'is_published': post.is_published,
            'created_at': post.created_at,
            'author': parser_author(post.author),
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
    post = await PostRespository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Post not found',
        )

    return parse_post(post)


@router.put(
    '/{post_id}', status_code=HTTPStatus.OK, response_model=PostPublicSchema
)
async def update_post(
    post_id: int,
    post_data: PostUpdateSchema,
    session: DBSession,
    current_author: CurrentAuthor,
):
    post = await PostRespository.get_by_id(session, post_id)
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

    post = await PostRespository.update(
        session,
        obj=post,
        title=post_data.title,
        subtitle=post_data.subtitle,
        content=post_data.content,
    )

    return parse_post(post)


@router.delete(
    '/{post_id}', status_code=HTTPStatus.OK, response_model=MessageSchema
)
async def delete_post(
    post_id: int, session: DBSession, current_author: CurrentAuthor
):
    post = await PostRespository.get_by_id(session, post_id)
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

    await PostRespository.delete(session, obj=post)
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
    post = await PostRespository.get_by_id(session, post_id)
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

    if post.is_published:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Post is already published',
        )

    publish_date = datetime.now()

    post = await PostRespository.update(
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

    return parse_post(post)


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
    post = await PostRespository.get_by_id(session, post_id)
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

    if not post.is_published:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Post is already unpublished',
        )

    post = await PostRespository.update(
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
    post = await PostRespository.get_by_id(session, post_id)
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

    extracted_tags = await TagRepository.find_or_create_multiple(
        session, tags=tags.tags
    )

    await PostRespository.add_tags(session, post, extracted_tags)

    return parse_post(post)
