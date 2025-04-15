from http import HTTPStatus

from sqlalchemy import event

from api.models.post import Post


def test_create_post_ok(client, profile, user_token):
    post_data = {
        'title': 'Test Post',
        'subtitle': 'Test Subtitle',
        'content': 'This is the content of the test post.',
    }

    response = client.post(
        '/posts/',
        json=post_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data['title'] == post_data['title']
    assert response_data['subtitle'] == post_data['subtitle']
    assert response_data['content'] == post_data['content']
    assert not response_data['is_published']
    assert len(response_data['tags']) == 0  # noqa: PLR2004


def test_create_post_conflict(client, profile, post, user_token):
    post_data = {
        'title': 'Test Post',
        'subtitle': 'Test Subtitle',
        'content': 'This is the content of the test post.',
    }

    def fake_slug(mapper, connection, target):
        target.slug = post.slug

    event.listen(Post, 'before_insert', fake_slug)

    response = client.post(
        '/posts/',
        json=post_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    event.remove(Post, 'before_insert', fake_slug)

    assert response.status_code == HTTPStatus.CONFLICT
    assert 'already exists' in response.json()['detail']


def test_get_posts_ok(client, post):
    response = client.get('/posts/')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['total_items'] == 1
    assert len(response_data['posts']) == 1
    assert response_data['posts'][0]['title'] == post.title
    assert response_data['posts'][0]['subtitle'] == post.subtitle


def test_get_posts_not_found(client):
    response = client.get('/posts/')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'No posts found'


def test_get_post_ok(client, post):
    response = client.get(f'/posts/{post.id}')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['title'] == post.title
    assert response_data['subtitle'] == post.subtitle
    assert response_data['content'] == post.content


def test_get_post_not_found(client):
    response = client.get('/posts/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Post not found'


def test_update_post_ok(client, post, user_token):
    updated_data = {
        'title': 'Updated Title',
        'subtitle': 'Updated Subtitle',
        'content': 'Updated content of the post.',
    }

    response = client.put(
        f'/posts/{post.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['title'] == updated_data['title']
    assert response_data['subtitle'] == updated_data['subtitle']
    assert response_data['content'] == updated_data['content']


def test_update_post_not_found(client, user_token, profile):
    updated_data = {
        'title': 'Updated Title',
        'subtitle': 'Updated Subtitle',
        'content': 'Updated content of the post.',
    }

    response = client.put(
        '/posts/999',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Post not found'


def test_update_post_forbidden(client, another_profile, post, user_token):
    updated_data = {
        'title': 'Updated Title',
        'subtitle': 'Updated Subtitle',
        'content': 'Updated content of the post.',
    }

    response = client.put(
        f'/posts/{post.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to update this post'
    )


def test_delete_post_ok(client, post, user_token):
    response = client.delete(
        f'/posts/{post.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'Post deleted'


def test_delete_post_not_found(client, user_token, profile):
    response = client.delete(
        '/posts/999',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Post not found'


def test_delete_post_forbidden(client, another_profile, post, user_token):
    response = client.delete(
        f'/posts/{post.id}',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to delete this post'
    )


def test_publish_post_ok(client, post, user_token):
    response = client.post(
        f'/posts/{post.id}/publish',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['is_published'] is True


def test_publish_post_not_found(client, user_token, profile):
    response = client.post(
        '/posts/999/publish',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Post not found'


def test_publish_post_forbidden(client, another_profile, post, user_token):
    response = client.post(
        f'/posts/{post.id}/publish',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to publish this post'
    )


def test_unpublish_post_ok(client, post, user_token):
    response = client.post(
        f'/posts/{post.id}/unpublish',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'Post unpublished'


def test_unpublish_post_not_found(client, user_token, profile):
    response = client.post(
        '/posts/999/unpublish',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Post not found'


def test_unpublish_post_forbidden(client, another_profile, post, user_token):
    response = client.post(
        f'/posts/{post.id}/unpublish',
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to unpublish this post'
    )


def test_add_tags_to_post_ok(client, post, user_token):
    tags = 'tag1, tag2'

    response = client.post(
        f'/posts/{post.id}/tags',
        json={'tags': tags},
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert len(response_data['tags']) == 2  # noqa: PLR2004
    tags_names = [tag['name'] for tag in response_data['tags']]
    assert 'tag1' in tags_names
    assert 'tag2' in tags_names


def test_add_tags_to_post_not_found(client, user_token, profile):
    tags = 'tag1, tag2'

    response = client.post(
        '/posts/999/tags',
        json={'tags': tags},
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Post not found'


def test_add_tags_to_post_forbidden(client, another_profile, post, user_token):
    tags = 'tag1, tag2'

    response = client.post(
        f'/posts/{post.id}/tags',
        json={'tags': tags},
        headers={'Authorization': f'Bearer {user_token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert (
        response.json()['detail']
        == 'You do not have permission to add tags to this post'
    )
