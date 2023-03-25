from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст (от лат. textus — ткань; сплетение, сочетание) — '
                 'зафиксированная на каком-либо материальном',
            group=cls.group,
        )

    def test_post_have_correct_object_names(self):
        # хотела сделать одним методом через subTest, но запуталась
        """Проверяем, что у post корректно работает __str__."""
        post = PostModelTest.post

        expected_name = post.text[:15]
        self.assertEqual(expected_name, str(post))

    def test_group_have_correct_object_names(self):
        """у group корректно работает __str__."""
        group = PostModelTest.group

        expected_name = group.title
        self.assertEqual(expected_name, str(group))

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Введите текст поста',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_help_text_group(self):
        """help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'description': 'Опишите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)
