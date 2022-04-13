from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase

from posts.models import Post

User = get_user_model()


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='Author_cache'),
            text='Тестовый текст cache')

    def setUp(self):
        self.guest_client = Client()

    def test_index_page_cache(self):
        '''Проверка кеширования главной страницы.'''
        response1 = self.guest_client.get(reverse('posts:index'))
        self.post.delete()
        response2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response1.content, response3.content)
