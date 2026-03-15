import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count_on_home_page(client, news_list):
    """Количество новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    assert news_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client, news_list):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news_list):
    """Комментарии на странице новости отсортированы по возрастанию."""
    url = reverse('news:detail', args=(news_list[0].id,))
    response = client.get(url)
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_comment_form_not_available_for_anonymous(client, news_list):
    """Форма комментария не доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news_list[0].id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_comment_form_available_for_author(author_client, news_list):
    """Форма комментария доступна авторизованному пользователю."""
    url = reverse('news:detail', args=(news_list[0].id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
