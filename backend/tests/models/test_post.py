import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.models.post import Post


@pytest.mark.asyncio
async def test_post_create_ok(session, profile, mock_db_time):
    with mock_db_time(model=Post) as time:
        post = Post(
            title='Test Post',
            subtitle='Test Subtitle',
            slug='test-post',
            content='This is the content of the test post.',
            author_id=profile.id,
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)

    db_post = await session.scalar(
        select(Post).filter(Post.slug == 'test-post')
    )

    assert db_post is not None
    assert db_post.id == post.id
    assert db_post.title == 'Test Post'
    assert db_post.subtitle == 'Test Subtitle'
    assert db_post.slug == 'test-post'
    assert db_post.content == 'This is the content of the test post.'
    assert db_post.is_published is False
    assert db_post.created_at == time
    assert db_post.updated_at == time
    assert db_post.published_at == time
    assert db_post.author_id == profile.id
    assert len(db_post.tags) == 0


@pytest.mark.asyncio
async def test_post_unique_slug_error(session, profile, post):
    duplicate_post = Post(
        title='Another Post',
        subtitle='Another Subtitle',
        slug=post.slug,
        content='This is another post content.',
        author_id=profile.id,
    )
    session.add(duplicate_post)

    with pytest.raises(IntegrityError) as e:
        await session.commit()

    assert 'slug' in str(e.value.orig)


@pytest.mark.asyncio
async def test_post_update_title_ok(session, post):
    post.title = 'Updated Title'
    await session.commit()
    await session.refresh(post)

    updated_post = await session.scalar(
        select(Post).filter(Post.id == post.id)
    )
    assert updated_post.title == 'Updated Title'


@pytest.mark.asyncio
async def test_post_update_content_ok(session, post):
    post.content = 'Updated content of the post.'
    await session.commit()
    await session.refresh(post)

    updated_post = await session.scalar(
        select(Post).filter(Post.id == post.id)
    )
    assert updated_post.content == 'Updated content of the post.'


@pytest.mark.asyncio
async def test_post_delete_ok(session, post):
    await session.delete(post)
    await session.commit()

    deleted_post = await session.scalar(
        select(Post).filter(Post.id == post.id)
    )
    assert deleted_post is None


@pytest.mark.asyncio
async def test_post_get_by_slug_ok(session, post):
    found_post = await session.scalar(
        select(Post).filter(Post.slug == post.slug)
    )

    assert found_post is not None
    assert found_post.id == post.id
    assert found_post.slug == post.slug


@pytest.mark.asyncio
async def test_post_get_by_slug_nonexistent(session):
    nonexistent_post = await session.scalar(
        select(Post).filter(Post.slug == 'nonexistent-slug')
    )

    assert nonexistent_post is None


@pytest.mark.asyncio
async def test_post_add_tags_ok(session, post, tag):
    post.tags.append(tag)
    await session.commit()
    await session.refresh(post)

    updated_post = await session.scalar(
        select(Post).filter(Post.id == post.id)
    )
    assert len(updated_post.tags) == 1
    assert updated_post.tags[0].id == tag.id
    assert updated_post.tags[0].name == tag.name


@pytest.mark.asyncio
async def test_post_remove_tags_ok(session, post, tag):
    post.tags.append(tag)
    await session.commit()
    await session.refresh(post)

    post.tags.remove(tag)
    await session.commit()
    await session.refresh(post)

    updated_post = await session.scalar(
        select(Post).filter(Post.id == post.id)
    )
    assert len(updated_post.tags) == 0
