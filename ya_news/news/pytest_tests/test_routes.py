from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from django.urls import reverse


pytestmark = pytest.mark.django_db


HOME_URL = lazy_fixture('home_url')
DETAIL_URL = lazy_fixture('detail_url')
EDIT_URL = lazy_fixture('edit_url')
DELETE_URL = lazy_fixture('delete_url')


@pytest.mark.parametrize(
    'client_fixture, url, expected_status',
    [
        (lazy_fixture('client'), HOME_URL, HTTPStatus.OK),
        (lazy_fixture('client'), DETAIL_URL, HTTPStatus.OK),
        (lazy_fixture('client'), EDIT_URL, HTTPStatus.NOT_FOUND),
        (lazy_fixture('client'), DELETE_URL, HTTPStatus.NOT_FOUND),

        (lazy_fixture('author_client'), HOME_URL, HTTPStatus.OK),
        (lazy_fixture('author_client'), DETAIL_URL, HTTPStatus.OK),
        (lazy_fixture('author_client'), EDIT_URL, HTTPStatus.OK),
        (lazy_fixture('author_client'), DELETE_URL, HTTPStatus.OK),
    ]
)
def universal_test_pages_status(client_fixture, url, expected_status):
    """
    Универсальный тест: проверяем статус-коды
    для разных клиентов и страниц.
    """
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name',
    (EDIT_URL, DELETE_URL)
)
def test_anonymous_user_redirected_to_login(client, comment, url_name):
    """Анонимный пользователь перенаправляется на страницу входа."""
    login_url = reverse('users:login')
    url = reverse(url_name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
