from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    group = models.ForeignKey(
        "Group",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name='Автор',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200, db_index=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите группу',
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Комментируемый пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name='Автор комментария',
    )
    text = models.TextField(verbose_name='Текст комментария')

    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )

    class Meta:
        constraints = models.UniqueConstraint(fields=['author', 'user'], name='unique_follower')
    