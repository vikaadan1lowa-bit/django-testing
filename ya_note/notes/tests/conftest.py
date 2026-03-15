from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseNoteTest(TestCase):
    """Базовый класс для тестов приложения notes."""

    NOTE_SLUG = 'test-slug'
    LIST_URL = reverse('notes:list')
    ADD_URL = reverse('notes:add')
    EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
    DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
    SUCCESS_URL = reverse('notes:success')
    SIGNUP_URL = reverse('users:signup')
    LOGIN_URL = reverse('users:login')

    @classmethod
    def setUpTestData(cls):
        """Создает тестовых пользователей и заметку для всех тестов класса."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.author_client = cls.client_class()
        cls.reader_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)
