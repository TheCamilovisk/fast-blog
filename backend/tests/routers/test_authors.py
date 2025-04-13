from http import HTTPStatus


def test_read_authors_ok(client, profile, user, another_user):
    response = client.get('/authors/')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['total_items'] == 1
    assert len(response_data['authors']) == 1
    assert response_data['authors'][0]['id'] == profile.id
    assert response_data['authors'][0]['username'] == profile.user.username
    assert response_data['authors'][0]['firstname'] == profile.firstname
    assert response_data['authors'][0]['lastname'] == profile.lastname


def test_read_author_ok(client, profile, user_token):
    response = client.get(
        f'/authors/{profile.user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['id'] == profile.id
    assert response_data['username'] == profile.user.username
    assert response_data['firstname'] == profile.firstname
    assert response_data['lastname'] == profile.lastname
    assert response_data['bio'] == profile.bio
    assert response_data['website'] == profile.website


def test_read_author_not_found(client, user_token):
    response = client.get(
        '/authors/999',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Author not found'


def test_read_author_forbidden(client, user_token, another_profile):
    response = client.get(
        f'/authors/{another_profile.user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this author'
    )


def test_create_author_ok(client, user, user_token):
    author_data = {
        'firstname': 'John',
        'lastname': 'Doe',
        'bio': 'This is a test bio',
        'website': 'https://example.com',
    }

    response = client.post(
        f'/authors/{user.id}',
        json=author_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data['firstname'] == author_data['firstname']
    assert response_data['lastname'] == author_data['lastname']
    assert response_data['bio'] == author_data['bio']
    assert response_data['website'] == author_data['website']


def test_create_author_conflict(client, profile, user_token):
    author_data = {
        'firstname': 'John',
        'lastname': 'Doe',
        'bio': 'This is a test bio',
        'website': 'https://example.com',
    }

    response = client.post(
        f'/authors/{profile.user.id}',
        json=author_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'Profile already exists.'


def test_create_author_forbidden(client, another_profile, user_token):
    author_data = {
        'firstname': 'John',
        'lastname': 'Doe',
        'bio': 'This is a test bio',
        'website': 'https://example.com',
    }

    response = client.post(
        f'/authors/{another_profile.id}',
        json=author_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this user'
    )


def test_update_author_ok(client, profile, user_token):
    updated_data = {
        'firstname': 'UpdatedFirstName',
        'lastname': 'UpdatedLastName',
        'bio': 'Updated bio',
        'website': 'https://updatedexample.com',
    }

    response = client.put(
        f'/authors/{profile.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['firstname'] == updated_data['firstname']
    assert response_data['lastname'] == updated_data['lastname']
    assert response_data['bio'] == updated_data['bio']
    assert response_data['website'] == updated_data['website']


def test_update_author_not_found(client, user_token):
    updated_data = {
        'firstname': 'UpdatedFirstName',
        'lastname': 'UpdatedLastName',
        'bio': 'Updated bio',
        'website': 'https://updatedexample.com',
    }

    response = client.put(
        '/authors/999',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Author not found'


def test_update_author_forbidden(client, another_profile, user_token):
    updated_data = {
        'firstname': 'UpdatedFirstName',
        'lastname': 'UpdatedLastName',
        'bio': 'Updated bio',
        'website': 'https://updatedexample.com',
    }

    response = client.put(
        f'/authors/{another_profile.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this author profile'
    )


def test_delete_author_ok(client, profile, user_token):
    response = client.delete(
        f'/authors/{profile.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'Author deleted successfully'


def test_delete_author_not_found(client, user_token):
    response = client.delete(
        '/authors/999',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Author not found'


def test_delete_author_forbidden(client, another_profile, user_token):
    response = client.delete(
        f'/authors/{another_profile.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this author profile'
    )
