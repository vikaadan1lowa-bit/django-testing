from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .test_content import BaseNoteTest

User = get_user_model()


class TestRoutes(BaseNoteTest):
    """Тесты доступности маршрутов приложения notes."""

    def test_pages_available_for_authenticated_user(self):
        """Авторизованный пользователь может открыть страницы приложения."""
        self.client.force_login(self.author)
        urls = [
            self.LIST_URL,
            self.ADD_URL,
            self.SUCCESS_URL,
            self.SIGNUP_URL,
            self.LOGIN_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def common_test_pages_status(self):
        """Проверяет доступность страниц для разных пользователей."""
        test_cases = [
            (self.client, reverse('notes:home'), HTTPStatus.OK),
            (self.client, self.SIGNUP_URL, HTTPStatus.OK),
            (self.client, self.LOGIN_URL, HTTPStatus.OK),
            (self.client, self.LIST_URL, HTTPStatus.FOUND),
            (self.client, self.ADD_URL, HTTPStatus.FOUND),
            (self.client, self.EDIT_URL, HTTPStatus.FOUND),
            (self.client, self.DELETE_URL, HTTPStatus.FOUND),
            (self.author_client, self.LIST_URL, HTTPStatus.OK),
            (self.author_client, self.ADD_URL, HTTPStatus.OK),
            (self.author_client, self.EDIT_URL, HTTPStatus.OK),
            (self.author_client, self.DELETE_URL, HTTPStatus.OK),
            (self.reader_client, self.EDIT_URL, HTTPStatus.NOT_FOUND),
            (self.reader_client, self.DELETE_URL, HTTPStatus.NOT_FOUND),
        ]
        for client, url, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = client.get(url)
                if expected_status == HTTPStatus.FOUND:
                    redirect_url = f'{self.LOGIN_URL}?next={url}'
                    self.assertRedirects(response, redirect_url)
                else:
                    self.assertEqual(response.status_code, expected_status)
