import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='Author',
                                            email='mail@mail.com',
                                            password='1234',
                                            first_name='John',
                                            last_name='Smith'),
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        text = response.context['text']
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image.name
        self.assertEqual(text, 'Последние обновления на сайте.')
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'Author')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        text = response.context['text']
        group = response.context['group']
        first_object = response.context['page_obj'][0]
        group_title = group.title
        group_description = group.description
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image.name
        self.assertEqual(group_title, 'Тестовый заголовок')
        self.assertEqual(group_description, 'Тестовый текст')
        self.assertEqual(text, 'Записи сообщества: test-slug')
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'Author')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        Follow.objects.create(
            user=self.user,
            author=self.post.author)
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Author'})
        )
        text = response.context['text']
        quantity = response.context['quantity']
        follow = response.context['following']
        author_object = response.context['author']
        author = author_object.username
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image.name
        self.assertEqual(text, 'Профайл пользователя John Smith')
        self.assertEqual(quantity, 1)
        self.assertEqual(author, 'Author')
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_author_0, 'Author')
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertEqual(follow, True)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'})
        )
        text = response.context['text']
        quantity = response.context['quantity']
        first_object = response.context['post']
        post_text = first_object.text
        post_author = first_object.author.username
        post_image = first_object.image.name
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(quantity, 1)
        self.assertEqual(post_text, 'Тестовый текст')
        self.assertEqual(post_author, 'Author')
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        self.user2 = self.post.author
        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PostCreateTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group1 = Group.objects.create(
            title='Тестовый заголовок1',
            description='Тестовый текст1',
            slug='test-slug1'
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок2',
            description='Тестовый текст2',
            slug='test-slug2'
        )
        cls.post1 = Post.objects.create(
            author=User.objects.create_user(username='Author',
                                            email='mail@mail.com',
                                            password='1234'),
            text='Тестовый текст1',
            group=cls.group1
        )

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_correct_index_grouplist_profile_follow(self):
        """Пост отображается на главной, на странице группы, в профайл
        и в ленте подписки."""
        Follow.objects.create(
            user=self.user,
            author=self.post1.author)
        reverse_list = [reverse('posts:index'),
                        reverse('posts:follow_index'),
                        reverse('posts:group_list',
                                kwargs={'slug': 'test-slug1'}),
                        reverse('posts:profile',
                                kwargs={'username': 'Author'})]
        for reverse_list in reverse_list:
            with self.subTest(reverse_list=reverse_list):
                response = self.authorized_client.get(reverse_list)
                post_res = response.context.get('page_obj')
                self.assertIn(self.post1, post_res)

    def test_post_create_correct_group(self):
        """Пост не отображается на странице чужой группы."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug2'}))
        post_res = response.context.get('page_obj')
        self.assertNotIn(self.post1, post_res)

    def test_follow_correct_follower(self):
        """Пост не отображается в ленте у тех, кто не подписан."""
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        post_res = response.context.get('page_obj')
        self.assertNotIn(self.post1, post_res)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        author = User.objects.create_user(username='Author',
                                          email='mail@mail.com',
                                          password='1234')
        posts: list = []
        for i in range(13):
            posts.append(Post(author=author,
                              text=f'Тестовый текст{i}',
                              group=cls.group))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Первая страница содержит 10 записей."""
        reverse_list = [reverse('posts:index'),
                        reverse('posts:group_list',
                                kwargs={'slug': 'test-slug'}),
                        reverse('posts:profile',
                                kwargs={'username': 'Author'})]
        for reverse_list in reverse_list:
            with self.subTest(reverse_list=reverse_list):
                response = self.client.get(reverse_list)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Вторая страница содержит 3 записи."""
        reverse_list = [reverse('posts:index'),
                        reverse('posts:group_list',
                                kwargs={'slug': 'test-slug'}),
                        reverse('posts:profile',
                                kwargs={'username': 'Author'})]
        for reverse_list in reverse_list:
            with self.subTest(reverse_list=reverse_list):
                response = self.client.get(reverse_list + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
