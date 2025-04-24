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


def test_refresh_token_ok(client, user):
    """Test successful refresh using a valid refresh token."""
    # Step 1: login to get refresh token
    login_response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    refresh_token = login_response.json()['refresh_token']

    # Step 2: use refresh token
    refresh_response = client.post(
        '/auth/refresh', json={'refresh_token': refresh_token}
    )

    assert refresh_response.status_code == HTTPStatus.OK
    data = refresh_response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_refresh_token_invalid_token(client):
    """Test refresh with an invalid refresh token."""
    response = client.post(
        '/auth/refresh', json={'refresh_token': 'invalid_token'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid refresh token'


def test_logout_ok(client, user):
    """Test logging out with a valid refresh token."""
    login_response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    refresh_token = login_response.json()['refresh_token']

    # Step 1: logout
    logout_response = client.post(
        '/auth/logout', json={'refresh_token': refresh_token}
    )
    assert logout_response.status_code == HTTPStatus.OK
    assert logout_response.json() == {'message': 'User logged out'}

    # Step 2: try to reuse the refresh token
    refresh_response = client.post(
        '/auth/refresh', json={'refresh_token': refresh_token}
    )
    assert refresh_response.status_code == HTTPStatus.UNAUTHORIZED
    assert refresh_response.json()['detail'] == 'Invalid refresh token'
