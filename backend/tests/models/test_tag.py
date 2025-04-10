from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.models.tag import Tag


def test_tag_create_ok(session, mock_db_time):
    with mock_db_time(model=Tag) as time:
        tag = Tag(name='TestTag')
        session.add(tag)
        session.commit()
        session.refresh(tag)

    db_tag = session.scalar(select(Tag).filter_by(name='TestTag'))

    assert db_tag is not None
    assert asdict(db_tag) == {
        'id': tag.id,
        'name': 'TestTag',
        'created_at': time,
        'updated_at': time,
    }


def test_tag_unique_name_error(session, tag):
    duplicate_tag = Tag(name=tag.name)
    session.add(duplicate_tag)

    with pytest.raises(IntegrityError) as e:
        session.commit()

    assert 'name' in str(e.value.orig)


def test_tag_update_name_ok(session, tag):
    tag.name = 'UpdatedTag'
    session.commit()
    session.refresh(tag)

    updated_tag = session.scalar(select(Tag).filter_by(id=tag.id))
    assert updated_tag.name == 'UpdatedTag'


def test_tag_delete_ok(session, tag):
    session.delete(tag)
    session.commit()

    deleted_tag = session.scalar(select(Tag).filter_by(id=tag.id))
    assert deleted_tag is None


def test_tag_get_by_name_ok(session, tag):
    found_tag = session.scalar(select(Tag).filter_by(name=tag.name))

    assert found_tag is not None
    assert found_tag.id == tag.id
    assert found_tag.name == tag.name


def test_tag_get_by_name_nonexistent(session):
    nonexistent_tag = session.scalar(
        select(Tag).filter_by(name='NonexistentTag')
    )

    assert nonexistent_tag is None
