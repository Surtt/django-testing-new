from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст'
BAD_WORD = 'редиска'
WARNING = 'Не ругайтесь!'


def test_anonymous_cannot_create_comment(client, news_detail_url):
    client.post(news_detail_url, {'text': COMMENT_TEXT})
    assert Comment.objects.count() == 0


def test_authorized_can_create_comment(
    author, author_client, news_detail_url, news
):
    author_client.post(news_detail_url, {'text': COMMENT_TEXT})
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


def test_author_redirected_to_comments_after_create(
    author_client, news_detail_url
):
    response = author_client.post(news_detail_url, {'text': COMMENT_TEXT})
    assertRedirects(response, f'{news_detail_url}#comments')


def test_author_redirected_to_comments_after_edit(
    author_client, comment_edit_url, news_detail_url
):
    response = author_client.post(comment_edit_url, {'text': NEW_COMMENT_TEXT})
    assertRedirects(response, f'{news_detail_url}#comments')


def test_author_redirected_to_comments_after_delete(
    author_client, comment_delete_url, news_detail_url
):
    response = author_client.post(comment_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')


def test_author_can_edit_comment(
    author, author_client, news, comment, comment_edit_url
):
    author_client.post(comment_edit_url, {'text': NEW_COMMENT_TEXT})
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_comment(author_client, comment_delete_url):
    author_client.post(comment_delete_url)
    assert Comment.objects.count() == 0


def test_reader_cannot_edit_foreign_comment(
    author, reader_client, news, comment, comment_edit_url
):
    original_text = comment.text
    response = reader_client.post(comment_edit_url, {'text': NEW_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_text
    assert comment.author == author
    assert comment.news == news


def test_reader_cannot_delete_foreign_comment(
    reader_client, comment, comment_delete_url
):
    response = reader_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get() == comment


@pytest.mark.parametrize('bad_word', (BAD_WORD, BAD_WORD.upper()))
def test_comment_with_bad_word_is_not_created(
    author_client, news_detail_url, bad_word
):
    response = author_client.post(
        news_detail_url, {'text': f'Какой {bad_word}!'}
    )
    assertFormError(response.context['form'], 'text', WARNING)
    assert Comment.objects.count() == 0
