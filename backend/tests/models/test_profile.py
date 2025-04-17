from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.models.profile import Profile


@pytest.mark.asyncio
async def test_profile_create_ok(session, user, mock_db_time):
    with mock_db_time(model=Profile) as time:
        profile = Profile(
            bio='This is a test bio',
            website='https://example.com',
            firstname='John',
            lastname='Doe',
            user_id=user.id,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    db_profile = await session.scalar(
        select(Profile).filter(Profile.user_id == user.id)
    )

    assert db_profile is not None
    assert asdict(db_profile) == {
        'id': profile.id,
        'bio': 'This is a test bio',
        'website': 'https://example.com',
        'firstname': 'John',
        'lastname': 'Doe',
        'created_at': time,
        'updated_at': time,
        'user_id': user.id,
        'posts': [],
    }


@pytest.mark.asyncio
async def test_profile_unique_user_id_error(session, user, profile):
    duplicate_profile = Profile(
        bio='Another bio',
        website='https://anotherexample.com',
        firstname='Jane',
        lastname='Smith',
        user_id=user.id,
    )
    session.add(duplicate_profile)

    with pytest.raises(IntegrityError) as e:
        await session.commit()

    assert 'user_id' in str(e.value.orig)


@pytest.mark.asyncio
async def test_profile_update_bio_ok(session, profile):
    profile.bio = 'Updated bio'
    await session.commit()
    await session.refresh(profile)

    updated_profile = await session.scalar(
        select(Profile).filter(Profile.id == profile.id)
    )
    assert updated_profile.bio == 'Updated bio'


@pytest.mark.asyncio
async def test_profile_update_website_ok(session, profile):
    profile.website = 'https://updatedexample.com'
    await session.commit()
    await session.refresh(profile)

    updated_profile = await session.scalar(
        select(Profile).filter(Profile.id == profile.id)
    )
    assert updated_profile.website == 'https://updatedexample.com'


@pytest.mark.asyncio
async def test_profile_update_firstname_ok(session, profile):
    profile.firstname = 'UpdatedFirstName'
    await session.commit()
    await session.refresh(profile)

    updated_profile = await session.scalar(
        select(Profile).filter(Profile.id == profile.id)
    )
    assert updated_profile.firstname == 'UpdatedFirstName'


@pytest.mark.asyncio
async def test_profile_update_lastname_ok(session, profile):
    profile.lastname = 'UpdatedLastName'
    await session.commit()
    await session.refresh(profile)

    updated_profile = await session.scalar(
        select(Profile).filter(Profile.id == profile.id)
    )
    assert updated_profile.lastname == 'UpdatedLastName'


@pytest.mark.asyncio
async def test_profile_delete_ok(session, profile):
    await session.delete(profile)
    await session.commit()

    deleted_profile = await session.scalar(
        select(Profile).filter(Profile.id == profile.id)
    )
    assert deleted_profile is None


@pytest.mark.asyncio
async def test_profile_get_by_user_id_ok(session, profile):
    found_profile = await session.scalar(
        select(Profile).filter(Profile.user_id == profile.user_id)
    )

    assert found_profile is not None
    assert found_profile.id == profile.id
    assert found_profile.user_id == profile.user_id


@pytest.mark.asyncio
async def test_profile_get_by_user_id_nonexistent(session):
    nonexistent_profile = await session.scalar(
        select(Profile).filter(Profile.user_id == 9999)  # noqa: PLR2004
    )

    assert nonexistent_profile is None
