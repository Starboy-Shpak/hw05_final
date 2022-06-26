from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='authorized_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            group=cls.group
        )
        cls.guest_url = (
            ('/', 'posts/index.html'),
            ('/group/test-group-slug/', 'posts/group_list.html'),
            ('/profile/authorized_user/', 'posts/profile.html'),
            (f'/posts/{PostsURLTest.post.id}/', 'posts/post_detail.html')
        )
        cls.auth_user_url = {
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{PostsURLTest.post.id}/edit/', 'posts/create_post.html')
        }

    def setUp(self):
        """Создаем двух пользователей."""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_url(self):
        """Проверка доступности страниц неавторизованному пользователю."""
        for url, template in PostsURLTest.guest_url:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_auth_url(self):
        """Проверка доступности страниц авторизованному пользователю."""
        for url, template in PostsURLTest.auth_user_url:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url_exists(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
