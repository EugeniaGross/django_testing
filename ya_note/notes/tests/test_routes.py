from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='author_1',
            author=cls.author,
        )
        cls.public_urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        cls.private_urls = (
            ('notes:detail', (cls.note.slug, )),
            ('notes:edit', (cls.note.slug, )),
            ('notes:delete', (cls.note.slug, )),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None)
        )

    def test_pages_availability_for_anonymous_user(self):
        """
        Домашняя страница, страница входа, выхода и регистрации
        доступны для анонимного пользователя.
        """
        for name in self.public_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_auth_user(self):
        """
        Страница добавления заметки, списка заметок и страница
        успешного добавления заметки доступны для авторизованных пользователей.
        """
        urls = (
            'notes:add',
            'notes:success',
            'notes:list',
        )
        for name in urls:
            with self.subTest(name=name):
                self.client.force_login(self.reader)
                url = reverse(name)
                response = response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_see_edit_and_delete(self):
        """
        Страница просмотра заметки, удаления и редактирования
        доступны для авторизованных пользователей.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete'
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Переадресация анонимных пользователей на страницу входа."""
        login_url = reverse('users:login')
        for name, args in self.private_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
