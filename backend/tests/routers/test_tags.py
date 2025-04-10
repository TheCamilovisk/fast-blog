from http import HTTPStatus

from api.models.tag import Tag


def test_list_tags_ok(client, tag):
    response = client.get('/tags/')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['total_items'] == 1
    assert len(response_data['tags']) == 1
    assert response_data['tags'][0]['id'] == tag.id
    assert response_data['tags'][0]['name'] == tag.name


def test_list_tags_with_pattern_ok(client, tag, session):
    another_tag = Tag(name='AnotherTag')
    session.add(another_tag)
    session.commit()

    response = client.get('/tags/?pattern=Another')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['total_items'] == 1
    assert len(response_data['tags']) == 1
    assert response_data['tags'][0]['id'] == another_tag.id
    assert response_data['tags'][0]['name'] == another_tag.name


def test_list_tags_with_pagination_ok(client, session):
    for i in range(1, 6):
        tag = Tag(name=f'Tag{i}')
        session.add(tag)
    session.commit()

    response = client.get('/tags/?limit=10&offset=0')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['total_items'] == 5  # noqa: PLR2004
    assert len(response_data['tags']) == 5  # noqa: PLR2004
    assert response_data['tags'][0]['name'] == 'Tag1'
    assert response_data['tags'][1]['name'] == 'Tag2'
    assert response_data['tags'][2]['name'] == 'Tag3'
    assert response_data['tags'][3]['name'] == 'Tag4'
    assert response_data['tags'][4]['name'] == 'Tag5'


def test_list_tags_no_results(client):
    response = client.get('/tags/')

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data['total_items'] == 0
    assert len(response_data['tags']) == 0
