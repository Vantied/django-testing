import pytest

from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
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
