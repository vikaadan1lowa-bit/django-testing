import pytest

from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects


def test_home_page_available_for_anonymous(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_available_for_anonymous(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_comment_pages_available_for_author(author_client, comment, name):
    """Страницы редактирования и удаления комментария доступны автору."""
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    reader_client,
    comment,
    name
):
    """Пользователь не может редактировать или удалять чужие комментарии."""
    url = reverse(name, args=(comment.id,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_anonymous_user_redirected_to_login(client, comment, name):
    """Анонимный пользователь перенаправляется на страницу входа."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup')
)
def test_auth_pages_available_for_anonymous(client, name):
    """Страницы доступные анонимному пользователю."""
    url = reverse(name)
    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code == HTTPStatus.FOUND
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
