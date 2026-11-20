from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


COMMENT_URLS = ('comment_edit_url', 'comment_delete_url')


@pytest.mark.parametrize(
    'url_fixture_name',
    ('news_home_url', 'news_detail_url', 'login_url', 'signup_url'),
)
def test_public_pages_are_accessible(client, request, url_fixture_name):
    url = request.getfixturevalue(url_fixture_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('url_fixture_name', COMMENT_URLS)
@pytest.mark.parametrize(
    'client_fixture_name, expected_status',
    (
        ('author_client', HTTPStatus.OK),
        ('reader_client', HTTPStatus.NOT_FOUND),
    ),
)
def test_comment_pages_access_by_user(
    request, url_fixture_name, client_fixture_name, expected_status
):
    url = request.getfixturevalue(url_fixture_name)
    user_client = request.getfixturevalue(client_fixture_name)
    response = user_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('url_fixture_name', COMMENT_URLS)
def test_anonymous_redirected_to_login(
    client, request, login_url, url_fixture_name
):
    url = request.getfixturevalue(url_fixture_name)
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')


def test_logout_by_post_clears_session(author_client, logout_url):
    assert '_auth_user_id' in author_client.session
    response = author_client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(client, logout_url):
    response = client.get(logout_url)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
