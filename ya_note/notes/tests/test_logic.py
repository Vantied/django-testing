from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from pytils.translit import slugify

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestLogic(TestCase):

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку"""
        url = reverse('notes:add')
        count_before = Note.objects.count()

        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), count_before + 1)

        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку"""
        url = reverse('notes:add')
        count_before = Note.objects.count()

        response = self.client.post(url, data=self.form_data)

        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), count_before)

    def test_not_unique_slug(self):
        """Нельзя создать заметку с уже существующим slug"""
        self.client.force_login(self.author)
        url = reverse('notes:add')

        self.form_data['slug'] = self.note.slug
        response = self.client.post(url, data=self.form_data)
        form = response.context['form']

        self.assertIsInstance(form, NoteForm)
        self.assertIn('slug', form.errors)
        self.assertIn(self.note.slug, str(form.errors['slug']))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Если slug не указан, он формируется автоматически через slugify"""
        url = reverse('notes:add')
        self.client.force_login(self.author)
        form_data = self.form_data.copy()
        form_data.pop('slug')

        count_before = Note.objects.count()
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), count_before + 1)

        new_note = Note.objects.get(title=form_data['title'])
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку"""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))

        self.note.refresh_from_db()

        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Проверяем, что чужую заметку нельзя редактировать"""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.not_author)
        response = self.client.post(url, data=self.form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку"""
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить чужую заметку"""
        self.client.force_login(self.not_author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
