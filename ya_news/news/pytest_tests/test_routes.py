from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, client_fixture, method, expected_status, check_redirect',
    [
        # Доступ анонимного пользователя
        ('news:home', None, 'client', 'get', HTTPStatus.OK, False),
        ('news:detail', 'news', 'client', 'get', HTTPStatus.OK, False),
        ('users:signup', None, 'client', 'get', HTTPStatus.OK, False),
        ('users:login', None, 'client', 'get', HTTPStatus.OK, False),
        ('users:logout', None, 'client', 'post', HTTPStatus.OK, False),

        # Автор комментария может редактировать и удалять
        ('news:edit', 'comment', 'author_client', 'get', HTTPStatus.OK, False),
        ('news:delete', 'comment', 'author_client', 'get',
         HTTPStatus.OK, False),

        # Аноним перенаправляется на логин
        ('news:edit', 'comment', 'client', 'get', HTTPStatus.FOUND, True),
        ('news:delete', 'comment', 'client', 'get', HTTPStatus.FOUND, True),

        # Другой пользователь получает 404
        ('news:edit', 'comment', 'not_author_client',
         'get', HTTPStatus.NOT_FOUND, False),
        ('news:delete', 'comment', 'not_author_client',
         'get', HTTPStatus.NOT_FOUND, False),
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

    arg = {
        'news': (news.id,),
        'comment': (comment.id,),
        None: None,
    }
    url = reverse(name, args=arg[args])
    response = getattr(client, method)(url)
    assert response.status_code == expected_status

    redirect_checks = {
        True: reverse('users:login'),
        False: None
    }
    expected_redirect_prefix = redirect_checks[check_redirect]
    if expected_redirect_prefix:
        assert response.url.startswith(expected_redirect_prefix)
