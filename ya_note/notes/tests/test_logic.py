from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

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

    def get_created_note(self, before_notes):
        """Возвращает новую заметку, появившуюся в БД после создания"""
        after_notes = set(Note.objects.all())
        new_notes = after_notes - before_notes
        self.assertEqual(len(new_notes), 1)
        return new_notes.pop()

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку"""
        url = reverse('notes:add')
        self.client.force_login(self.author)

        notes_before = set(Note.objects.all())
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        new_note = self.get_created_note(notes_before)
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

        self.assertFormError(
            response.context['form'],
            'slug',
            f'{self.note.slug}{WARNING}'
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Если slug не указан, он формируется автоматически через slugify"""
        url = reverse('notes:add')
        self.client.force_login(self.author)

        notes_before = set(Note.objects.all())
        response = self.client.post(url, data={
            'title': self.form_data['title'],
            'text': self.form_data['text']
        })
        self.assertRedirects(response, reverse('notes:success'))
        new_note = self.get_created_note(notes_before)
        max_length = Note._meta.get_field('slug').max_length
        expected_slug = slugify(self.form_data['title'])[:max_length]
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку"""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)

        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))

        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.title, self.form_data['title'])
        self.assertEqual(note_from_db.text, self.form_data['text'])
        self.assertEqual(note_from_db.slug, self.form_data['slug'])
        self.assertEqual(note_from_db.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        """Чужую заметку нельзя редактировать"""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.not_author)

        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)
        self.assertEqual(note_from_db.author, self.note.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку"""
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалить чужую заметку"""
        self.client.force_login(self.not_author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
