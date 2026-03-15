from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from .conftest import BaseNoteTest
from notes.models import Note

User = get_user_model()


class TestNoteLogic(BaseNoteTest):
    """Тесты логики создания заметок."""

    NOTE_TITLE = 'Тестовая заметка'
    NOTE_TEXT = 'Текст заметки'

    @classmethod
    def setUpTestData(cls):
        """Подготавливает данные для тестов логики заметок."""
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        expected_url = self.SUCCESS_URL
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.ADD_URL, data=self.form_data)
        expected_url = f'{self.LOGIN_URL}?next={self.ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Нельзя создать две заметки с одинаковым slug."""
        notes_count = Note.objects.count()
        response = self.author_client.post(self.ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count)
        self.assertFormError(
            response.context['form'],
            'slug',
            f"{self.form_data['slug']} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )

    def test_slug_is_generated_if_empty(self):
        """Если не заполнен slug, то он формируется автоматически."""
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        self.form_data.pop('slug')
        self.author_client.post(self.ADD_URL, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertNotEqual(notes_count_after, notes_count_before)
        note = Note.objects.get()
        expected_slug = slugify(self.NOTE_TITLE)
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_delete_note(self):
        """Автор заметки может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.DELETE_URL)
        self.assertRedirects(response, self.SUCCESS_URL)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count_before = Note.objects.count()
        response = self.reader_client.post(self.DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_author_can_edit_note(self):
        """Автор заметки может редактировать свою заметку."""
        note_before = Note.objects.get(id=self.note.id)
        response = self.author_client.post(self.EDIT_URL, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_URL)
        note_after = Note.objects.get(id=self.note.id)
        self.assertEqual(note_after.text, self.form_data['text'])
        self.assertEqual(note_after.title, self.form_data['title'])
        self.assertEqual(note_after.slug, self.NOTE_SLUG)
        self.assertEqual(note_after.author, note_before.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        note_before = Note.objects.get(id=self.note.id)
        response = self.reader_client.post(self.EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_after = Note.objects.get(id=self.note.id)
        self.assertEqual(note_after.text, note_before.text)
        self.assertEqual(note_after.title, note_before.title)
        self.assertEqual(note_after.slug, self.NOTE_SLUG)
        self.assertEqual(note_after.author, note_before.author)
