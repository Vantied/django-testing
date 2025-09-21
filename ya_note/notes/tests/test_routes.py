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

<<<<<<< HEAD
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

            # Анонимный пользователь должен перенаправляться на логин
            (reverse('notes:list'), self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:add'), self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:success'), self.client, 'get', HTTPStatus.FOUND),
            (reverse('notes:detail', args=(self.note.slug,)), self.client,
             'get', HTTPStatus.FOUND),
            (reverse('notes:edit', args=(self.note.slug,)), self.client,
             'get', HTTPStatus.FOUND),
            (reverse('notes:delete', args=(self.note.slug,)), self.client,
             'get', HTTPStatus.FOUND),
        ]

        for url, client, method, expected_status in test_cases:
            with self.subTest(url=url, client=client):
                response = getattr(client, method)(url)
                self.assertEqual(response.status_code, expected_status)

                # Для анонимного клиента проверяем правильность редиректа
                if expected_status == HTTPStatus.FOUND:
                    self.assertRedirects(response, f'{login_url}?next={url}')
=======
    def test_pages_availability_for_anonymous_user(self):
        """1 и 5 пункт"""
        urls = ('notes:home', 'users:login', 'users:signup', 'users:logout')

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """2 пункт"""
        urls = ('notes:list', 'notes:add', 'notes:success')
        self.client.force_login(self.author)

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        """3 пункт"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND),
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """4 пункт"""
        login_url = reverse('users:login')
        test_cases = (
            ('notes:detail', self.note),
            ('notes:edit', self.note),
            ('notes:delete', self.note),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )

        for name, note_object in test_cases:
            with self.subTest(page=name):
                if note_object is not None:
                    url = reverse(name, args=(note_object.slug,))
                else:
                    url = reverse(name)
                expected_redirect = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect,)
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
