from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(
        client,
        news,
        form_data,
        detail_url
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(detail_url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    form_data,
    detail_url
):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_bad_words_in_comment(
    author_client,
    news,
    form_data,
    detail_url
):
    """Комментарий с запрещёнными словами не публикуется."""
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'
    response = author_client.post(detail_url, data=form_data)
    assertFormError(
        response.context['form'],
        'text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client,
        comment,
        form_data,
        edit_url,
        detail_url
):
    """Автор комментария может редактировать свой комментарий."""
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == form_data['text']
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news
    assert comment.created == comment_from_db.created


def test_author_can_delete_comment(
        author_client,
        comment,
        delete_url,
        detail_url
):
    """Автор комментария может удалить свой комментарий."""
    response = author_client.post(delete_url)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
        not_author_client,
        comment,
        form_data,
        edit_url
):
    """Авторизованный пользователь не может редактировать чужой комментарий."""
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news
    assert comment.created == comment_from_db.created


def test_other_user_cant_delete_comment(
        not_author_client,
        comment,
        delete_url
):
    """Авторизованный пользователь не может удалить чужой комментарий."""
    response = not_author_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
