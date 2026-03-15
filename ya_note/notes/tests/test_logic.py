from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from .test_content import BaseNoteTest
from notes.models import Note

User = get_user_model()


class TestNoteLogic(BaseNoteTest):
    """Тесты логики создания заметок."""

    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'test-slug'

    def setUp(self):
        """Подготавливает данные для тестов логики заметок."""
        super().setUp()
        self.form_data = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': self.NOTE_SLUG,
        }
        self.add_url = self.ADD_URL
        self.edit_url = self.EDIT_URL
        self.delete_url = self.DELETE_URL

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(self.add_url, data=self.form_data)
        expected_url = self.SUCCESS_URL
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Нельзя создать две заметки с одинаковым slug."""
        notes_count = Note.objects.count()
        self.author_client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_slug_is_generated_if_empty(self):
        """Если не заполнен slug, то он формируется автоматически."""
        notes_count_before = Note.objects.count()
        self.form_data.pop('slug')
        self.author_client.post(self.add_url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertNotEqual(notes_count_after, notes_count_before)
        note = Note.objects.get(slug=slugify(self.NOTE_TITLE))
        expected_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Автор заметки может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_author_can_edit_note(self):
        """Автор заметки может редактировать свою заметку."""
        note_before = Note.objects.get(id=self.note.id)
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        note_after = Note.objects.get(id=self.note.id)
        self.assertEqual(note_after.text, self.form_data['text'])
        self.assertEqual(note_after.title, self.form_data['title'])
        self.assertEqual(note_after.slug, note_before.slug)
        self.assertEqual(note_after.author, note_before.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        note_before = Note.objects.get(id=self.note.id)
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=self.note.id)
        self.assertEqual(note_after.text, note_before.text)
        self.assertEqual(note_after.title, note_before.title)
        self.assertEqual(note_after.slug, note_before.slug)
        self.assertEqual(note_after.author, note_before.author)
