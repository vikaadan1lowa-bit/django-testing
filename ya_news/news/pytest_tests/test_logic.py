import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:add_comment', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    form_data
):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:add_comment', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('news:detail', args=(news.id,)))
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_bad_words_in_comment(
    author_client,
    news,
    form_data,
    settings
):
    """Комментарий с запрещёнными словами не публикуется."""
    bad_word = settings.BAD_WORDS[0]
    form_data['text'] = f'Это {bad_word} слово'
    url = reverse('news:add_comment', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertFormError(response.context['form'], 'text', errors=(WARNING,))
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, form_data):
    """Автор комментария может редактировать свой комментарий."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)

    assertRedirects(response, reverse('news:detail', args=(comment.news.id,)))
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    """Автор комментария может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response, reverse('news:detail', args=(comment.news.id,)))
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
