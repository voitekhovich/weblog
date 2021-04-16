from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()

TEST_USERNAME = 'TestUserName'
TEST_USERNAME2 = 'TestUserName2'
TEST_GROUP_SLUG = 'group_slug'

URL_HOMEPAGE = '/'
URL_GROUP_SLUG = f'/group/{TEST_GROUP_SLUG}/'
URL_NEW = '/new/'
URL_TEST_404 = '/test404/'
URL_FOLLOW = '/follow/'
URL_PROFILE_FOLLOW = f'/{TEST_USERNAME2}/follow/'
URL_PROFILE_UNFOLLOW = f'/{TEST_USERNAME2}/unfollow/'


class PostUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Group Title',
            slug=TEST_GROUP_SLUG,
        )
        cls.user = User.objects.create(username=TEST_USERNAME)
        Post.objects.create(
            author=cls.user,
            text="text test post",
        )

        cls.URL_PROFILE = f'/{TEST_USERNAME}/'
        cls.URL_PROFILE_POST = f'/{TEST_USERNAME}/1/'
        cls.URL_PROFILE_POST_EDIT = f'/{TEST_USERNAME}/1/edit/'

        cls.guest_urls = [
            URL_GROUP_SLUG,
            cls.URL_PROFILE,
            cls.URL_PROFILE_POST
        ]

    def setUp(self):
        self.guest_client = Client()
        self.user2 = User.objects.create(
            username=TEST_USERNAME2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user2)

    def test_homepage(self):
        response = self.guest_client.get(URL_HOMEPAGE)
        self.assertEqual(response.status_code, 200)

    def test_urls_exists_at_desired_location(self):
        """Страницы доступны любым пользователям."""
        urls_test = PostUrlsTests.guest_urls
        for url in urls_test:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_post_new_url_exists_at_desired_location(self):
        """Страница /new/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(URL_NEW)
        self.assertEqual(response.status_code, 200)

    def test_post_new_url_redirect_anonymous(self):
        """Страница /new/ перенаправляет анонимного пользователю."""
        response = self.guest_client.get(URL_NEW, follow=True)
        self.assertRedirects(response, ('/auth/login/?next=' + URL_NEW))

    def test_post_edit_url_exists_for_author(self):
        """Страница /edit/ доступна автору поста."""
        response = self.authorized_client.get(
            PostUrlsTests.URL_PROFILE_POST_EDIT)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_for_no_author(self):
        """Страница /edit/ не доступна авторизованному не автору поста."""
        response = self.authorized_client_2.get(
            PostUrlsTests.URL_PROFILE_POST_EDIT)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_exists_for_guest(self):
        """Страница /edit/ не доступна не авторизованному пользователю."""
        response = self.guest_client.get(
            PostUrlsTests.URL_PROFILE_POST_EDIT)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /edit/ перенаправляет анонимного пользователю."""
        response = self.guest_client.get(
            PostUrlsTests.URL_PROFILE_POST_EDIT, follow=True)
        self.assertRedirects(
            response, (f'/auth/login/?next=/{TEST_USERNAME}/1/edit/'))

    def test_post_edit_url_redirect_authorized(self):
        """Страница /edit/ перенаправляет анонимного пользователю."""
        response = self.authorized_client_2.get(
            PostUrlsTests.URL_PROFILE_POST_EDIT, follow=True)
        self.assertRedirects(response, PostUrlsTests.URL_PROFILE_POST)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls_names = {
            'index.html': URL_HOMEPAGE,
            'group.html': URL_GROUP_SLUG,
            'new.html': URL_NEW,
        }
        for template, reverse_name in templates_urls_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_edit_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.authorized_client.get(
            PostUrlsTests.URL_PROFILE_POST_EDIT)
        self.assertTemplateUsed(response, 'new.html')

    def test_post_edit_url_exists_for_author(self):
        """Возвращает ли сервер 404 если страница не найдена"""
        response = self.authorized_client.get(URL_TEST_404)
        self.assertEqual(response.status_code, 404)


class FollowUrlsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=TEST_USERNAME)
        cls.author = User.objects.create(username=TEST_USERNAME2)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_index_url(self):
        response = self.authorized_client.get(URL_FOLLOW)
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get(URL_FOLLOW)
        self.assertEqual(response.status_code, 302)

    def test_profile_follow_url(self):
        response = self.authorized_client.get(URL_PROFILE_FOLLOW)
        self.assertRedirects(response, (f'/{TEST_USERNAME2}/'))

        response = self.guest_client.get(URL_PROFILE_FOLLOW)
        self.assertRedirects(
            response, (f'/auth/login/?next={URL_PROFILE_FOLLOW}'))

    def test_profile_unfollow_url(self):
        response = self.authorized_client.get(URL_PROFILE_UNFOLLOW)
        self.assertRedirects(response, (f'/{TEST_USERNAME2}/'))

        response = self.guest_client.get(URL_PROFILE_UNFOLLOW)
        self.assertRedirects(
            response, (f'/auth/login/?next={URL_PROFILE_UNFOLLOW}'))


class CommentUrlsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=TEST_USERNAME)
        cls.author = User.objects.create(username=TEST_USERNAME2)
        cls.post = Post.objects.create(
            author=cls.author,
            text='test post text',
        )
        cls.URL_ADD_COMMENT = f'/{cls.author.username}/{cls.post.id}/comment/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        post = CommentUrlsTests.post
        url_add_comment = CommentUrlsTests.URL_ADD_COMMENT
        form_data = {
            'text': 'test comment', }
        response = self.authorized_client.post(
            url_add_comment, data=form_data, follow=True)
        self.assertRedirects(response, f'/{post.author.username}/{post.id}/')

        response = self.guest_client.post(
            url_add_comment, data=form_data, follow=True)
        self.assertRedirects(response, f'/auth/login/?next={url_add_comment}')
