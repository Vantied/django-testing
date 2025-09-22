from http import HTTPStatus

import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_fixture, client_fixture, method, expected_status',
    [
        # Доступ анонимного пользователя / публичные страницы
        ('news_home_url', 'client', 'get', HTTPStatus.OK),
        ('news_detail_url', 'client', 'get', HTTPStatus.OK),
        ('signup_url', 'client', 'get', HTTPStatus.OK),
        ('login_url', 'client', 'get', HTTPStatus.OK),
        ('logout_url', 'client', 'post', HTTPStatus.OK),

        # Автор комментария может редактировать и удалять
        ('comment_edit_url', 'author_client', 'get', HTTPStatus.OK),
        ('comment_delete_url', 'author_client', 'get', HTTPStatus.OK),

        # Другой пользователь получает 404
        ('comment_edit_url', 'not_author_client', 'get',
         HTTPStatus.NOT_FOUND),
        ('comment_delete_url', 'not_author_client', 'get',
         HTTPStatus.NOT_FOUND),
    ]
)
def test_status_codes(request, url_fixture, client_fixture, method,
                      expected_status):
    """
    Проверяем только статус-коды:
    - публичные страницы доступны анонимам;
    - автор комментария может редактировать/удалять;
    - аноним при попытке изменить/удалить получает редирект (302);
    - не-автор получает 404.
    """
    client = request.getfixturevalue(client_fixture)
    url = request.getfixturevalue(url_fixture)

    response = getattr(client, method)(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_fixture',
    (
        'comment_edit_url',
        'comment_delete_url',
    )
)
def test_anonymous_redirects(request, url_fixture, login_url):
    """
    Анонимный пользователь должен быть перенаправлен на страницу логина
    при попытке редактировать или удалить комментарий
    """
    client = request.getfixturevalue('client')
    url = request.getfixturevalue(url_fixture)

    response = client.get(url)
    expected_redirect = f'{login_url}?next={url}'

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect
