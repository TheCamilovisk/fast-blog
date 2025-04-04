from http import HTTPStatus


def test_get_root(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Hello World!!!"}
