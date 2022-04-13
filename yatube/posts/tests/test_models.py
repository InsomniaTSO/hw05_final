from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

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
            text='Тестовый пост__Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        text = str(post)
        self.assertEqual(text, 'Тестовый пост__')
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Напишите что-нибудь')
        group = self.group
        title = str(group)
        self.assertEqual(title, 'Тестовая группа')
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, 'Название группы')
        help_text = group._meta.get_field('description').help_text
        self.assertEqual(help_text, 'Дайте короткое описание группы')
