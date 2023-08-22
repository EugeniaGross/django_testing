from http import HTTPStatus
import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client,
    form_data,
    detail_url
):
    '''Анонимный пользователь не может создать комментарий.'''
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    author_client,
    form_data,
    detail_url,
    new,
    author
):
    '''Зарегистрированный пользователь может создать комментарий.'''
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == new
    assert comment.author == author


def test_user_cant_use_bad_words(
    author_client,
    bad_words_data,
    detail_url
):
    '''Пользователь не может использовать запрещенные слова.'''
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
    author_client,
    comment_id_for_args,
    detail_url
):
    '''Автор может удалить комментарий.'''
    url = reverse('news:delete', args=(comment_id_for_args))
    response = author_client.delete(url)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    admin_client,
    comment_id_for_args,
    new,
    author
):
    '''Не автор не может удалить комментарий.'''
    url = reverse('news:delete', args=(comment_id_for_args))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'Текст'
    assert comment.news == new
    assert comment.author == author


def test_author_can_edit_comment(
    author_client,
    comment_id_for_args,
    form_data, comment,
    id_for_args,
    new,
    author
):
    '''Автор может редактировать комментарий.'''
    url = reverse('news:edit', args=(comment_id_for_args))
    response = author_client.post(url, data=form_data)
    news_url = reverse('news:detail', args=(id_for_args))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == new
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
    admin_client,
    comment_id_for_args,
    form_data,
    comment,
    new,
    author
):
    '''Не автор не может редактировать комментарий.'''
    url = reverse('news:edit', args=(comment_id_for_args))
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
    assert comment.news == new
    assert comment.author == author
