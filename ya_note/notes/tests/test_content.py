from django.contrib.auth import get_user_model
from .conftest import BaseNoteTest

from notes.forms import NoteForm

User = get_user_model()


class TestNotesContent(BaseNoteTest):
    """Тесты контента приложения notes."""

    def common_test_note(self):
        """Проверяет видимость заметки для разных пользователей."""
        test_cases = [
            (self.author_client, self.assertIn),
            (self.reader_client, self.assertNotIn),
        ]
        for client, assert_func in test_cases:
            with self.subTest(client=client):
                response = client.get(self.LIST_URL)
                object_list = response.context['object_list']
                assert_func(self.note, object_list)

    def test_create_and_edit_note_page_contains_form(self):
        """На страницы создания и редактирования передаётся форма."""
        urls = (self.ADD_URL, self.EDIT_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
