from django.conf import settings

from news.forms import CommentForm


def test_news_count_on_home_page(client, news_list, home_url):
    """Количество новостей на главной странице."""
    response = client.get(home_url)
    news_list = response.context['object_list']
    assert news_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client, news_list, home_url):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(home_url)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, comments, detail_url):
    """Комментарии на странице новости отсортированы по возрастанию."""
    response = client.get(detail_url)
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    assert all_comments.count() > 0
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_comment_form_not_available_for_anonymous(client, detail_url):
    """Форма комментария не доступна анонимному пользователю."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_comment_form_available_for_author(author_client, detail_url):
    """Форма комментария доступна авторизованному пользователю."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
