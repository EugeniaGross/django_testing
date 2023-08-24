import pytest
from django.conf import settings


@pytest.mark.django_db
def test_news_count(client, news, home_url):
    """Количество новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news, home_url):
    """Сортировка новостей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, new, comments, detail_url):
    """Сортировка комментариев."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, comment_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_notes_list_for_different_users(
        new, parametrized_client, comment_in_list, detail_url
):
    """
    Форма для комментариев для зарегистрированного
    и незарегистированного пользователя.
    """
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is comment_in_list
