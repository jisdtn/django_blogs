from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User, Follow
from yatube.settings import AMOUNT_POSTS_NUMBER


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='Blanc')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse('posts:profile', args=[self.user]
                    ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=[self.post.pk]
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', args=[self.post.pk]
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))

        first_object = response.context['page_obj'][0]
        post_group_title_0 = first_object.group.title
        post_text_0 = first_object.text
        post_group_slug_0 = first_object.group.slug
        post_group_descr_0 = first_object.group.description
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image

        self.assertEqual(post_group_title_0, self.group.title)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_slug_0, self.group.slug)
        self.assertEqual(post_group_descr_0, self.group.description)
        self.assertEqual(post_author_0, self.user.username)
        self.assertEqual(post_image_0, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )

        object = response.context['page_obj']
        self.assertEqual(object[0].id, self.post.id)
        self.assertEqual(object[0].image, self.post.image)
        self.assertEqual(response.context['group'], self.post.group)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )

        object_post = response.context.get('post')
        self.assertEqual(object_post.author, self.post.author)
        self.assertEqual(object_post.text, self.post.text)
        self.assertEqual(object_post.group, self.post.group)
        self.assertEqual(object_post.image, self.post.image)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author}))
        object_post = response.context.get('page_obj')
        self.assertEqual(object_post[0].id, self.post.id)
        self.assertEqual(response.context['author'], self.post.author)
        self.assertEqual(object_post[0].image, self.post.image)

    def test_create_post_pages_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):

        for _ in range(AMOUNT_POSTS_NUMBER + 3):
            Post.objects.create(
                text='Text',
                author=self.user,
                group=self.group,
            )

        response = self.client.get(reverse('posts:index'))

        self.assertEqual(len(
            response.context['page_obj']), AMOUNT_POSTS_NUMBER)

    def test_second_page_contains_three_records(self):
        for _ in range(AMOUNT_POSTS_NUMBER + 3):
            Post.objects.create(
                text='Text',
                author=self.user,
                group=self.group,
            )

        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_cache_index(self):
        """Тестируем кэщ главной страницы"""
        cached_posts = self.guest_client.get(reverse('posts:index')).content
        Post.objects.all().delete()   
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(cached_posts, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(cached_posts, response.content)

class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Blanc')   
        cls.author = User.objects.create_user(username='author')
        cls.logged_in_client = Client()
        cls.logged_in_client.force_login(cls.user)


    def test_follow(self):
        subscription_url = reverse('posts:profile_follow', args=[self.author.username])
        response = self.logged_in_client.post(subscription_url)
        self.assertEqual(response.status_code, 302)

        subscription = Follow.objects.filter(
            author=self.author,
            user=self.user
        ).exists()
        self.assertIsNotNone(subscription)

    def test_unfollow(self):

        subscription_url = reverse('posts:profile_unfollow', args=[self.author.username])
        response = self.logged_in_client.post(subscription_url)
        self.assertEqual(response.status_code, 302)

        subscription = Follow.objects.filter(
            author=self.author,
            user=self.user
        ).exists()
        self.assertIsNotNone(subscription)

        
    def correct_post_feed(self):
        Follow.objects.create(
            author=self.author,
            user=self.user
        ) 
        response = self.user.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.contex['page_obj']), 1)

    def incorrect_post_feed(self):
        Follow.objects.create(
            author=self.author,
            user=self.user
        ) 
        response = self.user.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(len(response.contex['page_obj']), 1)
