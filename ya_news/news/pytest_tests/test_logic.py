import pytest

from http import HTTPStatus

from django.urls import reverse

from news.models import Comment
from news.forms import CommentForm, BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий"""
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Тестовый комментарий'}

    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authenticated_user_can_create_comment(author_client, news, author):
    """Авторизованный пользователь может отправить комментарий"""
    url = reverse('news:detail', args=(news.id,))
    comment_text = 'Тестовый комментарий'
    form_data = {'text': comment_text}

    author_client.post(url, data=form_data)

    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    """
    Комментарий с запрещёнными словами
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


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comments):
    """Автор комментария может удалить свой комментарий"""
    comment_to_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_delete.id,))
    initial_count = Comment.objects.count()

    author_client.delete(delete_url)

    assert Comment.objects.count() == initial_count - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(not_author_client, comments):
    """Авторизованный пользователь не может удалить чужой комментарий"""
    comment_to_try_delete = comments[0]
    delete_url = reverse('news:delete', args=(comment_to_try_delete.id,))
    initial_count = Comment.objects.count()

    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comments):
    """Автор комментария может редактировать свой комментарий"""
    comment = comments[0]
    edit_url = reverse('news:edit', args=(comment.id,))
    new_text = 'Обновлённый комментарий'
    form_data = {'text': new_text}

    author_client.post(edit_url, data=form_data)

    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(not_author_client, comments):
    """Авторизованный пользователь не может редактировать чужой комментарий"""
    comment = comments[0]
    edit_url = reverse('news:edit', args=(comment.id,))
    original_text = comment.text
    form_data = {'text': 'Попытка изменить'}

    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == original_text
