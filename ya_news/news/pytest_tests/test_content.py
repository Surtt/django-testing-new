from news.forms import CommentForm

from .constants import NEWS_ON_HOME_PAGE


def test_news_count_on_home_page_is_limited(client, news_home_url, news_batch):
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    assert response.context['object_list'].count() == NEWS_ON_HOME_PAGE


def test_news_are_ordered_from_newest_to_oldest(
    client, news_home_url, news_batch
):
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    dates = [news.date for news in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


def test_comments_are_ordered_from_oldest_to_newest(
    client, news_detail_url, comments
):
    response = client.get(news_detail_url)
    assert 'news' in response.context
    news = response.context['news']
    dates = [comment.created for comment in news.comment_set.all()]
    assert dates == sorted(dates)


def test_anonymous_client_has_no_comment_form(client, news_detail_url):
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_comment_form(author_client, news_detail_url):
    response = author_client.get(news_detail_url)
    assert isinstance(response.context['form'], CommentForm)
