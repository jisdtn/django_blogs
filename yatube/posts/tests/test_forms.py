import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='Blanc')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.author,
            group=cls.group,
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'group': self.group.id,
            'text': 'Текст',
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (f'/profile/{self.author}/'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """редактирует и сохраняет запись в Post."""

        form_data = {
            'group': self.group.id,
            'text': 'Текст',
            'image': self.uploaded,
        }

        self.url = reverse('posts:post_edit', args=(self.post.id,))

        response = self.author_client.post(
            self.url, data=form_data, follow=True)

        self.assertRedirects(
            response, reverse('posts:post_detail', args=(self.post.id,))
        )

        self.assertTrue(
            Post.objects.filter(
                text='Текст',
                group=self.group.id,
                image='posts/small.gif',
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Blanc')
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_can_add_comment(self):
        """Авторизованный пользователь может добавить коммент."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Текст комментария',
        }

        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )

        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Текст комментария',
            ).exists()
        )

    def test_client_cannot_add_comment(self):
        """Неавторизованный пользователь не может оставить ком."""
        comments_count = Comment.objects.count()

        form_data = {
            'text': 'Текст комментария',
        }

        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/comment/')
        )
