from http import HTTPStatus


def test_create_user_ok(client):
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data['username'] == user_data['username']
    assert response_data['email'] == user_data['email']
    assert 'id' in response_data


def test_create_user_conflict_error(client, user):
    user_data = {
        'username': user.username,
        'email': 'newuser@example.com',
        'password': 'password123',
    }

    response = client.post('/users/', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'Username already exists.'


def test_read_users_ok(client, user, another_user, user_token):
    response = client.get(
        '/users/', headers={'Authorization': f'Bearer {user_token}'}
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data['users']) == 2  # noqa: PLR2004
    assert any(u['username'] == user.username for u in response_data['users'])
    assert any(
        u['username'] == another_user.username for u in response_data['users']
    )


def test_read_user_ok(client, user, user_token):
    response = client.get(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {user_token}'}
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['username'] == user.username
    assert response_data['email'] == user.email


def test_read_user_forbidden_error(client, another_user, user_token):
    response = client.get(
        f'/users/{another_user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this user'
    )


def test_read_user_not_found_error(client, user_token):
    response = client.get(
        '/users/999', headers={'Authorization': f'Bearer {user_token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_update_username_ok(client, user, user_token):
    updated_data = {'username': 'updateduser'}

    response = client.put(
        f'/users/{user.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['username'] == updated_data['username']
    assert response_data['email'] == user.email


def test_update_username_conflict_error(
    client, user, another_user, user_token
):
    updated_data = {'username': another_user.username}

    response = client.put(
        f'/users/{user.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT

    detail = response.json()['detail']
    assert detail == 'Username already exists.'


def test_update_username_forbidden_error(client, another_user, user_token):
    updated_data = {'username': 'updateduser'}

    response = client.put(
        f'/users/{another_user.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this user'
    )


def test_update_user_not_found_error(client, user_token):
    updated_data = {'username': 'updateduser', 'email': 'updated@example.com'}

    response = client.put(
        '/users/999',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_update_email_ok(client, user, user_token):
    updated_data = {'email': 'updated@example.com'}

    response = client.put(
        f'/users/{user.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['username'] == user.username
    assert response_data['email'] == updated_data['email']


def test_update_email_conflict_error(client, user, another_user, user_token):
    updated_data = {'email': another_user.email}

    response = client.put(
        f'/users/{user.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == 'Email already exists.'


def test_update_email_forbidden_error(client, another_user, user_token):
    updated_data = {'email': 'updated@example.com'}

    response = client.put(
        f'/users/{another_user.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this user'
    )


def test_delete_user_ok(client, user, user_token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {user_token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'User deleted successfully'


def test_delete_user_not_found(client, user_token):
    response = client.delete(
        '/users/999', headers={'Authorization': f'Bearer {user_token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_delete_user_forbidden(client, another_user, user_token):
    response = client.delete(
        f'/users/{another_user.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to access this user'
    )
