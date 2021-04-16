from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEST_USERNAME = 'testUserName'
TEST_AUTHOR_USERNAME = 'testAuthorName'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
            username=TEST_USERNAME
        )
        cls.post = Post.objects.create(
            author=user,
            text='длинный тестовый текст поста'
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Сообщение',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'text': 'Текст поста',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str(self):
        post = PostModelTest.post
        length_str = len(post.__str__())
        self.assertEqual(length_str, 15)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='testGroupTitle',
        )

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'description': 'Описание',
        }
        for value, excepted in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, excepted)

    def test_help_text(self):
        group = GroupModelTest.group
        field_text_help = {
            'title': 'Вкратце о чём группа',
        }
        for value, expected in field_text_help.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_str(self):
        group = GroupModelTest.group
        title = group.title
        text_str = group.__str__()
        self.assertEqual(title, text_str)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
            username=TEST_USERNAME
        )
        post = Post.objects.create(
            author=user,
            text='длинный тестовый текст поста'
        )
        cls.comment = Comment.objects.create(
            text='test comment text',
            author=user,
            post=post
        )

    def test_verbose_name(self):
        comment = CommentModelTest.comment
        field_verboses = {
            'text': 'Комментарий',
            'created': 'Дата публикации',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_str(self):
        comment = CommentModelTest.comment
        date = comment.created.strftime('%d.%m.%Y %H:%M:%S')
        comment_str = f'{comment.author} | {date} | {comment.text[:15]}'
        self.assertEqual(comment_str, comment.__str__())


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create(
            username=TEST_USERNAME
        )
        author = User.objects.create(
            username=TEST_AUTHOR_USERNAME
        )
        cls.follow = Follow.objects.create(
            user=user,
            author=author,
        )

    def test_verbose_name(self):
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_str(self):
        follow = FollowModelTest.follow
        follow_str = f'{follow.user}-{follow.author}'
        self.assertEqual(follow_str, follow.__str__())
