from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='Author',
                                            email='mail@mail.com',
                                            password='1234'),
            text='Тестовый текст'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_accessible_urls(self):
        """Проверяем общедоступные страницы."""
        guest_urls = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}),
            reverse('posts:profile',
                    kwargs={'username': 'Author'}),
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}),
        ]
        for address in guest_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_for_404(self):
        """Тест ошибки 404."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_url_exists_authorized(self):
        """Страница /posts/profile/Author/follow/ доступна авторизованному
           пользователю."""
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Author'}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unfollow_url_exists_authorized(self):
        """Страница /posts/profile/Author/unfollow/ доступна авторизованному
           пользователю."""
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'Author'}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_added_url_exists_for_author(self):
        """Страница /posts/post.id/edit/ доступна автору Author."""
        self.user2 = self.post.author
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_list_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_task_detail_url_redirect_anonymous(self):
        """Страница /posts/post.id/edit/ перенаправляет анонимного
        пользователя.
        """
        response = self.guest_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_added_url_redirect_notauthor(self):
        """Страница /posts/post.id/edit/ перенаправляет не автора."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'Author'}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
            '/nonexist-page/': 'core/404.html',
        }
        self.user2 = self.post.author
        self.authorized_client.force_login(self.user2)
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
