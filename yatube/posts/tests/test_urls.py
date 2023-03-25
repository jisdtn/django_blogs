from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
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
            text='Текст (от лат. textus — ткань; сплетение, сочетание) — '
                 'зафиксированная на каком-либо материальном',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_open_pages(self):
        """Страницы доступны любому пользователю."""

        context = [('/', HTTPStatus.OK),
                   (f'/group/{self.group.slug}/', HTTPStatus.OK),
                   (f'/profile/{self.user.username}/', HTTPStatus.OK),
                   (f'/posts/{self.post.id}/', HTTPStatus.OK),
                   ('/unexisting_page/', HTTPStatus.NOT_FOUND),
                   ]

        for url, status_code in context:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_create_post_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_edit_post_url_redirect_anonymous_authorized(self):
        """Страница posts/<int:post_id>/edit/ перенаправляет анонимного
        и авторизованного пользователя."""
        if self.user != self.post.author:
            response = self.authorized_client.get(
                f'/posts/{self.post.id}/edit/', follow=True)
            self.assertRedirects(
                response, (f'/auth/login/?next=/posts/{self.post.id}/edit/'))

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
