from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCreateNote(TestCase):

    TITLE = 'Название'
    TEXT = 'Текст'
    SLUG = 'text_1'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': cls.TITLE,
            'text': cls.TEXT,
            'slug': cls.SLUG,
        }

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.guest_client = Client()

    def test_anonymous_user_cant_create_note(self):
        self.guest_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)

    def test_not_unique_slug(self):
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=self.form_data['slug'],
            author=self.user,
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.TITLE)
        self.assertEqual(new_note.slug, expected_slug)


class TestEditDeleteNote(TestCase):

    TITLE = 'Название'
    NEW_TITLE = 'Новое название'
    TEXT = 'Текст'
    NEW_TEXT = 'Новый текст'
    SLUG = 'text_1'
    NEW_SLUG = 'new_text_1'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, self.NEW_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)
        self.assertEqual(self.note.author, self.author)
