from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNoteLogic(TestCase):
    """Тесты логики создания заметок."""
    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'test-slug'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов создания заметок."""
        cls.user = User.objects.create(username='Автор')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }
        cls.add_url = reverse('notes:add')

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку"""
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Нельзя создать две заметки с одинаковым slug"""
        Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug=self.NOTE_SLUG,
            author=self.user
        )
        notes_count = Note.objects.count()
        self.auth_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_slug_is_generated_if_empty(self):
        """Если не заполнен slug, то он формируется автоматически."""
        form_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': ''
        }
        self.auth_client.post(self.add_url, data=form_data)
        note = Note.objects.get()
        expected_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    """Тесты редактирования и удаления заметок."""

    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновленный текст'

    @classmethod
    def setUpTestData(cls):
        """Подготовка данных для тестов редактирования и удаления."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заметка',
            text=cls.NOTE_TEXT,
            slug='test-slug',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': 'Заметка',
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }

    def test_author_can_delete_note(self):
        """Автор заметки может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Автор заметки может редактировать свою заметку."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
