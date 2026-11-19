from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup'),
)
def test_public_pages_are_accessible(client, name):
    response = client.get(reverse(name))
    assert response.status_code == HTTPStatus.OK


def test_news_detail_page_is_accessible(client, news_detail_url):
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_private_comment_pages_are_accessible_for_author(
    comment, author_client, name
):
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_private_comment_pages_not_found_for_reader(
    comment, reader_client, name
):
    url = reverse(name, args=(comment.pk,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_anonymous_redirected_to_login(comment, client, login_url, name):
    url = reverse(name, args=(comment.pk,))
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')


def test_logout_accepts_post_request(author_client, logout_url):
    assert '_auth_user_id' in author_client.session
    response = author_client.post(logout_url)
    assert response.status_code == HTTPStatus.OK
    assert '_auth_user_id' not in author_client.session


def test_logout_rejects_get_request(client, logout_url):
    response = client.get(logout_url)
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
