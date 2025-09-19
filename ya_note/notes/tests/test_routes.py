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
