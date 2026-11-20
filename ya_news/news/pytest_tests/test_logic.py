from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый текст'
BAD_WORD = 'редиска'
WARNING = 'Не ругайтесь!'


def assert_comment_unchanged(comment):
    """Поля комментария в БД совпадают с исходными значениями."""
    comment_after = Comment.objects.get(pk=comment.pk)
    assert comment_after.text == comment.text
    assert comment_after.author == comment.author
    assert comment_after.news == comment.news


def test_anonymous_cannot_create_comment(client, news_detail_url, login_url):
    comments_before = Comment.objects.count()
    response = client.post(news_detail_url, {'text': COMMENT_TEXT})
    assertRedirects(response, f'{login_url}?next={news_detail_url}')
    assert Comment.objects.count() == comments_before


def test_authorized_can_create_comment(
    author, author_client, news, news_detail_url
):
    form_data = {'text': COMMENT_TEXT}
    existing_pks = set(Comment.objects.values_list('pk', flat=True))
    author_client.post(news_detail_url, form_data)
    new_comments = Comment.objects.exclude(pk__in=existing_pks)
    assert new_comments.count() == 1
    comment = new_comments.get()
    assert comment.text == form_data['text']
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


def test_author_can_edit_comment(author_client, comment, comment_edit_url):
    form_data = {'text': NEW_COMMENT_TEXT}
    comments_before = Comment.objects.count()
    author_client.post(comment_edit_url, form_data)
    assert Comment.objects.count() == comments_before
    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == form_data['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_author_can_delete_comment(author_client, comment, comment_delete_url):
    comments_before = Comment.objects.count()
    author_client.post(comment_delete_url)
    assert Comment.objects.count() == comments_before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.parametrize(
    'name, form_data',
    (
        ('news:edit', {'text': NEW_COMMENT_TEXT}),
        ('news:delete', None),
    ),
    ids=('edit', 'delete'),
)
def test_reader_cannot_change_foreign_comment(
    reader_client, comment, name, form_data
):
    url = reverse(name, args=(comment.pk,))
    comments_before = Comment.objects.count()
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    assert_comment_unchanged(comment)


@pytest.mark.parametrize('bad_word', (BAD_WORD, BAD_WORD.upper()))
def test_comment_with_bad_word_is_not_created(
    author_client, news_detail_url, bad_word
):
    comments_before = Comment.objects.count()
    response = author_client.post(
        news_detail_url, {'text': f'Какой {bad_word}!'}
    )
    assert 'form' in response.context
    assertFormError(response.context['form'], 'text', WARNING)
    assert Comment.objects.count() == comments_before
