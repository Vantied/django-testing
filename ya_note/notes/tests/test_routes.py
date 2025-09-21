from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = self.client_class()
        self.author_client.force_login(self.author)
        self.not_author_client = self.client_class()
        self.not_author_client.force_login(self.not_author)

    def test_pages_availability(self):
        """Тест доступности всех страниц для разных типов пользователей"""
        login_url = reverse('users:login')

        test_cases = [
            # Главная и auth-страницы доступны всем
            (reverse('notes:home'), self.client, 'get', HTTPStatus.OK),
            (reverse('users:login'), self.client, 'get', HTTPStatus.OK),
            (reverse('users:signup'), self.client, 'get', HTTPStatus.OK),
            (reverse('users:logout'), self.client, 'post', HTTPStatus.OK),

            # Авторизованный пользователь автор заметки
            (reverse('notes:list'), self.author_client, 'get', HTTPStatus.OK),
            (reverse('notes:add'), self.author_client, 'get', HTTPStatus.OK),
            (reverse('notes:success'), self.author_client,
             'get', HTTPStatus.OK),

            # Страницы своей заметки
            (reverse('notes:detail', args=(self.note.slug,)),
             self.author_client, 'get', HTTPStatus.OK),
            (reverse('notes:edit', args=(self.note.slug,)),
             self.author_client, 'get', HTTPStatus.OK),
            (reverse('notes:delete', args=(self.note.slug,)),
             self.author_client, 'get', HTTPStatus.OK),

            # Авторизованный пользователь не автор заметки
            (reverse('notes:detail', args=(self.note.slug,)),
             self.not_author_client, 'get', HTTPStatus.NOT_FOUND),
            (reverse('notes:edit', args=(self.note.slug,)),
             self.not_author_client, 'get', HTTPStatus.NOT_FOUND),
            (reverse('notes:delete', args=(self.note.slug,)),
             self.not_author_client, 'get', HTTPStatus.NOT_FOUND),

            # Анонимный пользователь: должен перенаправляться на логин
            (reverse('notes:list'), self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:add'), self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:success'), self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:detail', args=(self.note.slug,)),
             self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:edit', args=(self.note.slug,)),
             self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:delete', args=(self.note.slug,)),
             self.client, 'get', HTTPStatus.FOUND),
        ]

        for url, client, method, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_status)

                # Для анонимного клиента проверяем правильность редиректа
                if expected_status == HTTPStatus.FOUND:
                    self.assertRedirects(response, f'{login_url}?next={url}')
