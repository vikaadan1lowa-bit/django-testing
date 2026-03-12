from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesContent(TestCase):
    """Тесты контента приложения notes."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_object_list(self):
        """Отдельная заметка передаётся в object_list."""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_of_other_users_not_in_list(self):
        """В список заметок пользователя не попадают чужие заметки."""
        other_note = Note.objects.create(
            title='Чужая заметка',
            text='Текст',
            slug='other-slug',
            author=self.reader
        )
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(other_note, object_list)

    def test_create_and_edit_note_page_contains_form(self):
        """На страницы создания и редактирования передаётся форма."""
        self.client.force_login(self.author)
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
