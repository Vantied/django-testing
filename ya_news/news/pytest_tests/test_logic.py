<<<<<<< HEAD
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING
=======
import pytest

from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import CommentForm, BAD_WORDS, WARNING
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий"""
    url = reverse('news:detail', args=(news.id,))
<<<<<<< HEAD
    existing_ids = set(Comment.objects.values_list('id', flat=True))

    client.post(url, data={'text': 'Тестовый комментарий'})

    new_ids = set(Comment.objects.values_list('id', flat=True))
    assert new_ids == existing_ids
=======
    form_data = {'text': 'Тестовый комментарий'}

    client.post(url, data=form_data)
    assert Comment.objects.count() == 0
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f


@pytest.mark.django_db
def test_authenticated_user_can_create_comment(author_client, news, author):
    """Авторизованный пользователь может отправить комментарий"""
    url = reverse('news:detail', args=(news.id,))
<<<<<<< HEAD
    existing_ids = set(Comment.objects.values_list('id', flat=True))
    author_client.post(url, data={'text': 'Тестовый комментарий'})

    new_ids = set(Comment.objects.values_list('id', flat=True)) - existing_ids
    assert len(new_ids) == 1

    new_comment_id = new_ids.pop()
    comment = Comment.objects.get(id=new_comment_id)
    assert comment.text == 'Тестовый комментарий'
=======
    comment_text = 'Тестовый комментарий'
    form_data = {'text': comment_text}

    author_client.post(url, data=form_data)

    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_text
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """
    Комментарий с запрещёнными словами
<<<<<<< HEAD
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
=======
    не публикуется, форма возвращает ошибку
    """
    url = reverse('news:detail', args=(news.id,))
    bad_text = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    form_data = {'text': bad_text}

    response = author_client.post(url, data=form_data)

    form = response.context['form']
    assert isinstance(form, CommentForm)
    assert 'text' in form.errors
    assert WARNING in str(form.errors['text'])
    assert Comment.objects.count() == 0
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comments):
    """Автор комментария может удалить свой комментарий"""
    comment_to_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_delete.id,))
<<<<<<< HEAD

    author_client.delete(delete_url)
    assert not Comment.objects.filter(id=comment_to_delete.id).exists()
=======
    initial_count = Comment.objects.count()

    author_client.delete(delete_url)

    assert Comment.objects.count() == initial_count - 1
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comments):
<<<<<<< HEAD
    """Пользователь не может удалить чужой комментарий"""
    comment_to_try_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_try_delete.id,))

    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment_to_try_delete.id).exists()
=======
    """Авторизованный пользователь не может удалить чужой комментарий"""
    comment_to_try_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_try_delete.id,))
    initial_count = Comment.objects.count()

    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    assert Comment.objects.count() == initial_count
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comments):
    """Автор комментария может редактировать свой комментарий"""
    comment = comments[0]
    edit_url = reverse('news:edit', args=(comment.id,))
    new_text = 'Обновлённый комментарий'
<<<<<<< HEAD

    author_client.post(edit_url, data={'text': new_text})
    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == new_text
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author
=======
    form_data = {'text': new_text}

    author_client.post(edit_url, data=form_data)

    comment.refresh_from_db()
    assert comment.text == new_text
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(not_author_client, comments):
<<<<<<< HEAD
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
=======
    """Авторизованный пользователь не может редактировать чужой комментарий"""
    comment = comments[0]
    edit_url = reverse('news:edit', args=(comment.id,))
    original_text = comment.text
    form_data = {'text': 'Попытка изменить'}

    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == original_text
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
