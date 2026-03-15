from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

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

    def setUp(self):
        """Создает авторизованных клиентов."""
        self.author_client = self.client_class()
        self.reader_client = self.client_class()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)


class TestNotesContent(BaseNoteTest):
    """Тесты контента приложения notes."""

    def common_test_note(self):
        """Проверяет видимость заметки для разных пользователей."""
        with self.subTest(client='author'):
            response = self.author_client.get(self.LIST_URL)
            object_list = response.context['object_list']
            self.assertIn(self.note, object_list)
        with self.subTest(client='reader'):
            response = self.reader_client.get(self.LIST_URL)
            object_list = response.context['object_list']
            self.assertNotIn(self.note, object_list)

    def test_create_and_edit_note_page_contains_form(self):
        """На страницы создания и редактирования передаётся форма."""
        urls = (self.ADD_URL, self.EDIT_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
