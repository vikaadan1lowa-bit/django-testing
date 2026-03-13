import pytest
from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    form_data
):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_bad_words_in_comment(
    author_client,
    news,
    form_data
):
    """Комментарий с запрещёнными словами не публикуется."""
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, form_data):
    """Автор комментария может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Автор комментария может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_edit_comment(not_author_client, comment, form_data):
    """Авторизованный пользователь не может редактировать чужой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


@pytest.mark.django_db
def test_other_user_cant_delete_comment(not_author_client, comment):
    """Авторизованный пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
