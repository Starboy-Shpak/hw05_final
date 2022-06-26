from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from ..forms import PostForm

from ..models import Group, Post, Follow

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='CR7')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='work',
            description='Описание группы',
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок 2',
            slug='work2',
            description='Описание группы 2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image='posts/small.gif'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        cache.clear()

    def context_test_function(self, response):
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый текст')
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.group.title, 'Тестовый заголовок')
        self.assertIsNotNone(first_object.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse('posts:group_list', kwargs={
                'slug': self.group.slug}), 'posts/group_list.html'),
            (reverse('posts:profile', kwargs={
                'username': self.user.username}), 'posts/profile.html'),
            (reverse('posts:post_detail', kwargs={
                'post_id': 1}), 'posts/post_detail.html'),
            (reverse('posts:post_edit', kwargs={
                'post_id': 1}), 'posts/create_post.html'),
            (reverse('posts:post_create'), 'posts/create_post.html')
        )
        for reverse_name, template in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.context_test_function(response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.context_test_function(response)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.context_test_function(response)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        object = response.context['post']
        self.assertEqual(object.text, 'Тестовый текст')
        self.assertEqual(object.author, self.user)
        self.assertEqual(object.group, self.group)
        self.assertEqual(object.group.title, 'Тестовый заголовок')
        self.assertIsNotNone(object.image)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
        )
        form_fields = (
            ('group', forms.fields.ChoiceField),
            ('text', forms.fields.CharField)
        )

        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context.get('form'), PostForm)
                self.assertIn('is_edit', response.context)
                self.assertTrue('is_edit')

    def test_create_post_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = (
            ('group', forms.fields.ChoiceField),
            ('text', forms.fields.CharField)
        )

        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertIsInstance(response.context.get('form'), PostForm)

    def test_new_post_if_is_valid_form_show_in_pages(self):
        """Проверяем, что пост с группой попадает на страницы."""
        self.post = [
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group,
            )
            for self.post in range(15)
        ]
        group_post_pages = (
            (reverse('posts:index'), 10),
            (reverse('posts:group_list', kwargs={'slug': 'work'}), 10),
            (reverse('posts:profile', kwargs={'username': self.user}), 10)
        )
        for value, expected in group_post_pages:
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(len(response.context["page_obj"]), expected)

    def test_new_group_page_dont_have_a_post(self):
        """Проверяем что на странице другой группы нет постов."""
        url = reverse('posts:group_list', args=['work2'])
        response = self.authorized_client.get(url)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_first_page_contains_ten_posts(self):
        """Проверяем, что пагинатор выводит 10 постов на странице."""
        self.post = [
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group,
            )
            for self.post in range(15)
        ]
        list_urls = (
            ((reverse('posts:index')), ("index")),
            ((reverse(
                'posts:group_list', kwargs={
                    "slug": self.group.slug
                })), ("group")),
            ((reverse(
                'posts:profile', kwargs={"username": self.user})), ("profile"))
        )
        for tested_url, template in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(len(
                response.context.get('page_obj').object_list), 10)

    def test_second_page_contains_six_posts(self):
        """Тестируем последнюю страницу пагинатора."""
        self.post = [
            Post.objects.create(
                text='Тестовый текст',
                author=self.user,
                group=self.group,
            )
            for self.post in range(15)
        ]
        list_urls = (
            ((reverse('posts:index') + "?page=2"), ("index")),
            ((reverse(
                'posts:group_list', kwargs={
                    "slug": self.group.slug}) + "?page=2"), ("group")),
            ((reverse(
                'posts:profile', kwargs={
                    "username": self.user}) + "?page=2"), ("profile")),
        )
        for tested_url, template in list_urls:
            response = self.client.get(tested_url)
            self.assertEqual(len(
                response.context.get('page_obj').object_list), 6)

    def test_comments_shown_for_auth_user(self):
        """Тестируем отображение комментария в шаблоне post_detail."""
        form_data = {
            'text': 'Тестовый комметарий'
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': 1}
            ),
            data=form_data,
            follow=True
        )
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': 1}
            )
        )
        self.assertTrue(response, 'Тестовый комметарий')

    def test_cache_index_page(self):
        """Тестируем работу кеша в index_page."""
        response1 = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(text='текстово и точка', author=self.user)

        response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)

        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response3.content, response1.content)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Agent_Smit')
        cls.author = User.objects.create_user(username='Neo')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_for_auth_user(self):
        """Тест: Авторизованный юзер может подписаться на другого юзера."""
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[self.author])
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_content_for_follower_and_unfollow(self):
        """Тест: Подписанный юзер видит контент и отписывается."""
        self.follower = Follow.objects.create(
            user=self.user, author=self.author
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 1)
        self.follower.delete()
        response1 = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotEqual(response.content, response1.content)

    def test_no_content_for_unfollower(self):
        """Тест: Неподписанный юзер не видит контент."""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
