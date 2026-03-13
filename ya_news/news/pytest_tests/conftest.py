import pytest
from django.test import Client
from django.utils import timezone
from news.models import News, Comment


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
    now = timezone.now()
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )
    comment.created = now
    comment.save()
    return comment


@pytest.fixture
def reader_client(django_user_model):
    """Авторизованный пользователь, который не является автором комментария."""
    user = django_user_model.objects.create(username='Читатель')
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def form_data():
    """Данные для создания/редактирования комментария."""
    return {
        'text': 'Тестовый комментарий'
    }
