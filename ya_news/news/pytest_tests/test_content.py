import pytest

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from news.forms import CommentForm
from news.models import Comment, News


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    """Количество новостей на главной странице."""
    News.objects.bulk_create(
        News(title=f'Новость {i}', text='Просто текст.')
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_by_date(client):
    """Новости отсортированы от самой свежей к самой старой."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {i}',
            text='Просто текст.',
            date=today - timedelta(days=1)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    url = reverse('news:home')
    response = client.get(url)
    news_list = response.context['object_list']
    all_dates = [news.date for news in news_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news, author_client):
    """Комментарии на странице новости отсортированы по возрастанию."""
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author_client.user,
            text=f'Комментарий {i}'
        )
        comment.created = now + timedelta(days=1)
        comment.save()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    )
)
def test_comment_form_availability(news, parametrized_client, form_in_context):
    """Форма комментария доступна только авторизованному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_context
    if form_in_context:
        assert isinstance(response.context['form'], CommentForm)
