<<<<<<< HEAD
from http import HTTPStatus

import pytest
=======
import pytest

from http import HTTPStatus

>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
<<<<<<< HEAD
    'name, args, client_fixture, method, expected_status, check_redirect',
    [
        # Доступ анонимного пользователя
        ('news:home', None, 'client', 'get', HTTPStatus.OK, False),
        ('news:detail', 'news', 'client', 'get', HTTPStatus.OK, False),
        ('users:signup', None, 'client', 'get', HTTPStatus.OK, False),
        ('users:login', None, 'client', 'get', HTTPStatus.OK, False),
        ('users:logout', None, 'client', 'post', HTTPStatus.OK, False),

        # Автор комментария может редактировать и удалять
        ('news:edit', 'comment', 'author_client', 'get',
         HTTPStatus.OK, False),
        ('news:delete', 'comment', 'author_client', 'get',
         HTTPStatus.OK, False),

        # Аноним перенаправляется на логин
        ('news:edit', 'comment', 'client', 'get', HTTPStatus.FOUND, True),
        ('news:delete', 'comment', 'client', 'get', HTTPStatus.FOUND, True),

        # Другой пользователь получает 404
        ('news:edit', 'comment', 'not_author_client', 'get',
         HTTPStatus.NOT_FOUND, False),
        ('news:delete', 'comment', 'not_author_client', 'get',
         HTTPStatus.NOT_FOUND, False),
    ]
)
def test_status_codes_and_redirects(
    request,
    name,
    args,
    client_fixture,
    method,
    expected_status,
    check_redirect,
    news,
    comment
):
    """
    Проверяем доступ к страницам:
    Анонимный пользователь видит публичные страницы и логин/логаут
    Автор комментария может редактировать и удалять свой комментарий
    Аноним перенаправляется на страницу логина при попытке изменять/удалить
    Пользователь получает 404 при попытке изменять/удалить чужой комментарий
    """
    client = request.getfixturevalue(client_fixture)

    arg_map = {
        'news': (news.id,),
        'comment': (comment.id,),
        None: None,
    }
    url = reverse(name, args=arg_map[args])
    response = getattr(client, method)(url)
    assert response.status_code == expected_status

    redirect_checks = {
        True: reverse('users:login'),
        False: None
    }
    expected_redirect_prefix = redirect_checks[check_redirect]
    if expected_redirect_prefix:
        assert response.url.startswith(expected_redirect_prefix)
=======
    'name, args',
    [
        ('news:home', False),
        ('news:detail', True),
        ('users:signup', False),
        ('users:login', False),
        ('users:logout', False),
    ]
)
def test_pages_accessible_to_anonymous(client, news, name, args):
    """Страницы новостей и аутентификации доступны анонимному пользователю."""
    args = (news.id,) if args else None
    url = reverse(name, args=args)

    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_author_can_access_edit_and_delete(author_client, comment, name):
    """
    Страницы удаления и редактирования комментария
    доступны автору комментария
    """
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_anonymous_redirected_to_login(client, comment, name):
    """
    Анонимный пользователь перенаправляется на страницу
    логина при попытке редактировать/удалить комментарий
    """
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(login_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_other_user_gets_404(not_author_client, comment, name):
    """
    Другой авторизованный пользователь
    не может редактировать или удалять чужие комментарии
    """
    url = reverse(name, args=(comment.id,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
