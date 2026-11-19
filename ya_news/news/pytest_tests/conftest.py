from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

NEWS_LIMIT = getattr(settings, 'NEWS_COUNT_ON_HOME_PAGE', 10)
COMMENTS_COUNT = 5


@pytest.fixture
def author(django_user_model, db):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def reader(django_user_model, db):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, db):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader, db):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(
        title='Название новости',
        text='Текст новости',
    )


@pytest.fixture
def comment(news, author, db):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def news_batch(db):
    today = timezone.now().date()
    return News.objects.bulk_create(
        [
            News(
                title=f'Новость {i}',
                text=f'Текст новости {i}',
                date=today + timedelta(days=i),
            )
            for i in range(NEWS_LIMIT + 1)
        ]
    )


@pytest.fixture
def comments(news, author, db):
    now = timezone.now()
    result = []
    for i in range(COMMENTS_COUNT):
        item = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        item.created = now - timedelta(days=i)
        item.save()
        result.append(item)
    return result


@pytest.fixture
def news_home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')
