from http import HTTPStatus


def test_login_for_access_token_ok(client, user):
    """Test successful login and token generation."""
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert 'access_token' in response_data
    assert response_data['token_type'] == 'bearer'


def test_login_for_access_token_invalid_password_error(client, user):
    """Test login with an invalid password."""
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password + 'wrong',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


def test_login_for_access_token_invalid_email_error(client):
    """Test login with an invalid email."""
    response = client.post(
        '/auth/token',
        data={'username': 'invalid@example.com', 'password': 'password123'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}
