from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls.base import reverse

from posts.models import Follow, Group, Post

User = get_user_model()

TEST_USERNAME = 'TestUserName'
TEST_GROUP_SLUG = 'group_slug'

TEST_USER1 = 'testUser1'
TEST_USER2 = 'testUser2'

VIEW_INDEX_NAME = 'index'
VIEW_NAME_POST = 'post'
VIEW_NAME_NEW_POST = 'new_post'
VIEW_NAME_POST_EDIT = 'post_edit'
VIEW_NAME_ADD_COMMENT = 'add_comment'

PAGE_PROFILE_FOLLOW = 'profile_follow'
PAGE_PROFILE_UNFOLLOW = 'profile_unfollow'
PAGE_PROFILE = 'profile'


class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=TEST_USERNAME)
        cls.group = Group.objects.create(
            title='test group',
            slug=TEST_GROUP_SLUG,
        )
        Post.objects.create(
            author=cls.user,
            text='Post test text',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test text',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse(VIEW_NAME_NEW_POST),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(VIEW_INDEX_NAME))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                id=post_count + 1,
                text='Test text',
                group_id=PostCreateFormTests.group.id,
            ).exists()
        )

    def test_update_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'The new post text',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(reverse(
            VIEW_NAME_POST_EDIT,
            kwargs={'username': TEST_USERNAME, 'post_id': '1'}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            VIEW_NAME_POST, kwargs={'username': TEST_USERNAME,
                                    'post_id': '1'}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                id=1,
                text='The new post text',
                group_id=PostCreateFormTests.group.id,
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=TEST_USERNAME)
        cls.testUser1 = User.objects.create(username=TEST_USER1)
        cls.post = Post.objects.create(
            author=cls.testUser1,
            text='new text of this post'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_new_comment(self):
        """Только авторизированный пользователь может
        комментировать посты."""
        post = CommentCreateFormTests.post
        post_comments_count_before = post.comments.count()
        form_data = {'text': 'test comment for post', }
        response = self.authorized_client.post(reverse(
            VIEW_NAME_ADD_COMMENT,
            kwargs={
                'username': post.author.username,
                'post_id': post.id, }),
            data=form_data, follow=True)
        post_comments_count_after = post.comments.count()
        self.assertRedirects(response, reverse(
            VIEW_NAME_POST, kwargs={
                'username': post.author.username,
                'post_id': post.id, }))
        self.assertEqual(post_comments_count_after,
                         post_comments_count_before + 1)

    def test_new_comment_for_guest(self):
        """Не авторизированный пользователь не может
        комментировать посты."""
        post = CommentCreateFormTests.post
        post_comments_count_before = post.comments.count()
        form_data = {'text': 'test comment for post', }
        response = self.guest_client.post(reverse(
            VIEW_NAME_ADD_COMMENT,
            kwargs={
                'username': post.author.username,
                'post_id': post.id, }),
            data=form_data, follow=True)
        post_comments_count_after = post.comments.count()
        self.assertEqual(post_comments_count_after,
                         post_comments_count_before)
        self.assertRedirects(response,
                             (f'/auth/login/?next=/{post.author.username}/'
                              f'{post.id}/comment/'))


class FollowFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=TEST_USERNAME)
        cls.testUser1 = User.objects.create(username=TEST_USER1)
        cls.testUser2 = User.objects.create(username=TEST_USER2)

        Follow.objects.create(
            user=cls.user,
            author=cls.testUser2,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_subscribe(self):
        """Авторизованный пользователь может подписываться
        на других пользователей"""
        response = self.authorized_client.post(reverse(
            PAGE_PROFILE_FOLLOW, kwargs={'username': TEST_USER1}))
        self.assertRedirects(response, reverse(
            PAGE_PROFILE, kwargs={'username': TEST_USER1}))
        self.assertTrue(
            Follow.objects.filter(
                user=FollowFormTest.user,
                author=FollowFormTest.testUser1,
            ).exists()
        )

    def test_unsubscribe(self):
        """Авторизованный пользователь может удалять
        пользователей из подписок."""
        response = self.authorized_client.post(reverse(
            PAGE_PROFILE_UNFOLLOW, kwargs={'username': TEST_USER2}))
        self.assertRedirects(response, reverse(
            PAGE_PROFILE, kwargs={'username': TEST_USER2}))
        self.assertFalse(
            Follow.objects.filter(
                user=FollowFormTest.user,
                author=FollowFormTest.testUser2,
            ).exists()
        )

    def test_new_post_for_subscribe_and_unsubscribe(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него."""
        Post.objects.create(
            author=FollowFormTest.testUser2,
            text='new text of this post'
        )
        self.assertTrue(
            Post.objects.filter(
                author__following__user=FollowFormTest.user).exists())
        self.assertFalse(
            Post.objects.filter(
                author__following__user=FollowFormTest.testUser1).exists())
