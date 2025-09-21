from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий"""
    url = reverse('news:detail', args=(news.id,))
    existing_ids = set(Comment.objects.values_list('id', flat=True))

    client.post(url, data={'text': 'Тестовый комментарий'})

    new_ids = set(Comment.objects.values_list('id', flat=True))
    assert new_ids == existing_ids


@pytest.mark.django_db
def test_authenticated_user_can_create_comment(author_client, news, author):
    """Авторизованный пользователь может отправить комментарий"""
    url = reverse('news:detail', args=(news.id,))
    existing_ids = set(Comment.objects.values_list('id', flat=True))
    author_client.post(url, data={'text': 'Тестовый комментарий'})

    new_ids = set(Comment.objects.values_list('id', flat=True)) - existing_ids
    assert len(new_ids) == 1

    new_comment_id = new_ids.pop()
    comment = Comment.objects.get(id=new_comment_id)
    assert comment.text == 'Тестовый комментарий'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """
    Комментарий с запрещёнными словами
    не публикуется и возвращает ошибку валидации
    """
    url = reverse('news:detail', args=(news.id,))
    bad_text = f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'
    existing_ids = set(Comment.objects.values_list('id', flat=True))

    response = author_client.post(url, data={'text': bad_text})
    form = response.context['form']
    assertFormError(form, field='text', errors=WARNING)

    new_ids = set(Comment.objects.values_list('id', flat=True))
    assert new_ids == existing_ids


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comments):
    """Автор комментария может удалить свой комментарий"""
    comment_to_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_delete.id,))

    author_client.delete(delete_url)
    assert not Comment.objects.filter(id=comment_to_delete.id).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comments):
    """Пользователь не может удалить чужой комментарий"""
    comment_to_try_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_try_delete.id,))

    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment_to_try_delete.id).exists()


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comments):
    """Автор комментария может редактировать свой комментарий"""
    comment = comments[0]
    edit_url = reverse('news:edit', args=(comment.id,))
    new_text = 'Обновлённый комментарий'

    author_client.post(edit_url, data={'text': new_text})
    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == new_text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(not_author_client, comments):
    """Пользователь не может редактировать чужой комментарий"""
    comment = comments[0]
    edit_url = reverse('news:edit', args=(comment.id,))

    response = not_author_client.post(
        edit_url, data={'text': 'Попытка изменить'})
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.news == comment.news
    assert unchanged_comment.author == comment.author
