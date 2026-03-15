from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Включаем автоматический доступ к БД для всех тестов."""
    pass


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def author(django_user_model):
    """Создаёт пользователя, который будет автором комментариев/новостей."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """
    Создаёт пользователя, который не является
    автором комментариев/новостей.
    """
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Используется для тестирования действий, доступных автору."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """
    Используется для тестирования доступа
    к чужим комментариям или новостям.
    """
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создаём тестовую новость."""
    return News.objects.create(
        title='Тестовая новость',
        text='Текст новости'
    )


@pytest.fixture
def comment(news, author):
    """Создаём комментарий к новости."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )
    return comment


@pytest.fixture
def form_data():
    """Данные для создания/редактирования комментария."""
    return {
        'text': 'Обновлённый комментарий'
    }


@pytest.fixture
def news_list():
    """Создаёт список новостей для тестов."""
    today = timezone.now()
    news_objects = [
        News(
            title=f'Новость {i}',
            text='Просто текст.',
            date=today - timedelta(days=i)
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_objects)


@pytest.fixture
def comments(news, author):
    """Создаёт 10 комментариев к новости."""
    comment_list = []
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}',
        )
        comment.created = now - timedelta(days=i)
        comment.save()
        comment_list.append(comment)
