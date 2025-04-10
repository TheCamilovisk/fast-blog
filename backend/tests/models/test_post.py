import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.models.post import Post


def test_post_create_ok(session, profile, mock_db_time):
    with mock_db_time(model=Post) as time:
        post = Post(
            title='Test Post',
            subtitle='Test Subtitle',
            slug='test-post',
            content='This is the content of the test post.',
            author_id=profile.id,
        )
        session.add(post)
        session.commit()
        session.refresh(post)

    db_post = session.scalar(select(Post).filter_by(slug='test-post'))

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


def test_post_unique_slug_error(session, profile, post):
    duplicate_post = Post(
        title='Another Post',
        subtitle='Another Subtitle',
        slug=post.slug,
        content='This is another post content.',
        author_id=profile.id,
    )
    session.add(duplicate_post)

    with pytest.raises(IntegrityError) as e:
        session.commit()

    assert 'slug' in str(e.value.orig)


def test_post_update_title_ok(session, post):
    post.title = 'Updated Title'
    session.commit()
    session.refresh(post)

    updated_post = session.scalar(select(Post).filter_by(id=post.id))
    assert updated_post.title == 'Updated Title'


def test_post_update_content_ok(session, post):
    post.content = 'Updated content of the post.'
    session.commit()
    session.refresh(post)

    updated_post = session.scalar(select(Post).filter_by(id=post.id))
    assert updated_post.content == 'Updated content of the post.'


def test_post_delete_ok(session, post):
    session.delete(post)
    session.commit()

    deleted_post = session.scalar(select(Post).filter_by(id=post.id))
    assert deleted_post is None


def test_post_get_by_slug_ok(session, post):
    found_post = session.scalar(select(Post).filter_by(slug=post.slug))

    assert found_post is not None
    assert found_post.id == post.id
    assert found_post.slug == post.slug


def test_post_get_by_slug_nonexistent(session):
    nonexistent_post = session.scalar(
        select(Post).filter_by(slug='nonexistent-slug')
    )

    assert nonexistent_post is None


def test_post_add_tags_ok(session, post, tag):
    post.tags.append(tag)
    session.commit()
    session.refresh(post)

    updated_post = session.scalar(select(Post).filter_by(id=post.id))
    assert len(updated_post.tags) == 1
    assert updated_post.tags[0].id == tag.id
    assert updated_post.tags[0].name == tag.name


def test_post_remove_tags_ok(session, post, tag):
    post.tags.append(tag)
    session.commit()
    session.refresh(post)

    post.tags.remove(tag)
    session.commit()
    session.refresh(post)

    updated_post = session.scalar(select(Post).filter_by(id=post.id))
    assert len(updated_post.tags) == 0
