from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

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

    def test_notes_list_for_different_users(self):
        """1 и 2 пункт"""
        users_checks = (
            (self.author, True),
            (self.not_author, False),
        )
        url = reverse('notes:list')

        for user, note_in_list in users_checks:
            self.client.force_login(user)
            with self.subTest(user=user.username):
                response = self.client.get(url)
                object_list = response.context['object_list']
                if note_in_list:
                    self.assertIn(self.note, object_list,)
                else:
                    self.assertNotIn(self.note, object_list,)

    def test_pages_contains_form(self):
        """3 пунтк"""
        test_cases = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)

        for name, args in test_cases:
            with self.subTest(page=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
