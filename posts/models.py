from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint
from pytils.translit import slugify

User = get_user_model()


class Group(models.Model):

    title = models.CharField(verbose_name='Название группы',
                             max_length=200,
                             help_text='Вкратце о чём группа')
    slug = models.SlugField('URL', unique=True, blank=True)
    description = models.TextField('Описание')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        super().save(*args, **kwargs)


class Post(models.Model):

    text = models.TextField(verbose_name='Сообщение', help_text='Текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='posts',)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True,
                              verbose_name='Группа',
                              related_name='posts')
    image = models.ImageField('Изображение', upload_to='posts/',
                              blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):

    text = models.TextField(verbose_name='Комментарий')
    created = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        date = self.created.strftime('%d.%m.%Y %H:%M:%S')
        return f'{self.author} | {date} | {self.text[:15]}'


class Follow(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='following')

    def __str__(self):
        return f'{self.user}-{self.author}'

    class Meta:
        UniqueConstraint(fields=('user', 'author'), name='unique_following')
