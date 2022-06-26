from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тот момент, когда "прикольно" перерасло в борщ:)',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        expected_names = (
            (self.post, self.post.text[:15]),
            (self.group, f'Группа - {self.group.title}')
        )
        for model, expected_value in expected_names:
            with self.subTest(model=model):
                self.assertEqual(expected_value, str(model))
