import datetime as dt
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()

TEST_USERNAME = 'pushkin'
TEST_GROUP_SLUG = 'group_slug'
TEST_GROUP_OTHER_SLUG = 'other_group_slug'

TEST_USER1 = 'testUser1'
TEST_USER2 = 'testUser2'

PAGE_INDEX = 'index'
PAGE_GROUP = 'group'
PAGE_POST_EDIT = 'post_edit'
PAGE_POST = 'post'
PAGE_PROFILE = 'profile'
PAGE_NEW_POST = 'new_post'


class PostsPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        small_jpg = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.jpg',
            content=small_jpg,
            content_type='image/jpg'
        )

        cls.user = User.objects.create(
            username=TEST_USERNAME,
            first_name='Alex',
            last_name='Pushkin'
        )
        cls.group = Group.objects.create(
            title='Group Title',
            slug=TEST_GROUP_SLUG,
            description='Group Test Description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='testPostText',
            pub_date=dt.datetime.now(),
            group=cls.group,
            image=uploaded,
        )
        Group.objects.create(
            title='Other Group Title',
            slug=TEST_GROUP_OTHER_SLUG,
            description='Other Group Test Description'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_context(self, post):
        self.assertEqual(post.text, PostsPagesTests.post.text)
        self.assertEqual(post.pub_date, PostsPagesTests.post.pub_date)
        self.assertEqual(post.author.get_full_name(),
                         PostsPagesTests.post.author.get_full_name())
        self.assertEqual(post.image, PostsPagesTests.post.image)

    def test_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'index.html': reverse(PAGE_INDEX),
            'new.html': reverse(PAGE_NEW_POST),
            'group.html':
                reverse(PAGE_GROUP, kwargs={'slug': TEST_GROUP_SLUG})}
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(PAGE_INDEX))
        self.check_post_context(response.context['page'][0])

    def test_group_slug_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(PAGE_GROUP, kwargs={'slug': TEST_GROUP_SLUG}))
        group = response.context['group']
        self.assertEqual(group.title, PostsPagesTests.group.title)
        self.assertEqual(group.slug, PostsPagesTests.group.slug)
        self.assertEqual(group.description, PostsPagesTests.group.description)
        self.check_post_context(response.context['page'][0])

    def test_new_post_pages_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_pages_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        username = PostsPagesTests.user.username
        post_id = PostsPagesTests.post.id
        response = self.authorized_client.get(
            reverse(PAGE_POST_EDIT, kwargs={'username': username,
                                            'post_id': post_id, }))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_username_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        username = PostsPagesTests.user.username
        response = self.authorized_client.get(
            reverse(PAGE_PROFILE, kwargs={'username': username}))
        self.check_post_context(response.context['page'][0])

    def test_username_post_page_show_correct_context(self):
        """Шаблон username/post сформирован с правильным контекстом."""
        username = PostsPagesTests.user.username
        response = self.authorized_client.get(
            reverse(PAGE_POST, kwargs={'username': username,
                                       'post_id': PostsPagesTests.post.id, }))
        self.check_post_context(response.context['post'])

    def test_new_post_on_group_sl(self):
        """Новый пост с группой отображается на главной странице"""
        """Новый пост с группой отображается на странице группы"""
        """Новый пост с группой не отображается на странице другой группы"""
        index_response = self.authorized_client.get(reverse(PAGE_INDEX))
        group_response = self.authorized_client.get(
            reverse(PAGE_GROUP, kwargs={'slug': TEST_GROUP_SLUG}))
        other_group_response = self.authorized_client.get(
            reverse(PAGE_GROUP, kwargs={'slug': TEST_GROUP_OTHER_SLUG}))

        self.assertEqual(
            index_response.context['page'][0].text, PostsPagesTests.post.text)
        self.assertEqual(
            group_response.context['page'][0].text, PostsPagesTests.post.text)
        self.assertEqual(len(other_group_response.context['page']), 0)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=TEST_USERNAME,
            first_name='Alex',
            last_name='Pushkin'
        )
        group = Group.objects.create(
            title='testGroup',
            slug=TEST_GROUP_SLUG)
        for i in range(13, 0, -1):
            Post.objects.create(
                author=cls.user,
                text=f'Test {i} Text',
                group=group
            )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse(PAGE_INDEX))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse(PAGE_INDEX) + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)

    def test_home_page_containse_records(self):
        """На 2-ой странице index сформирован правильный контекст."""
        response = self.client.get(reverse(PAGE_INDEX) + '?page=2')
        posts = response.context.get('page')
        count = 10
        for post in posts:
            with self.subTest():
                count += 1
                self.assertEqual(post.text, f'Test {count} Text')

    def test_group_page_containse_ten_records(self):
        response = self.client.get(
            reverse(PAGE_GROUP, kwargs={'slug': TEST_GROUP_SLUG}))
        self.assertEqual(len(response.context.get('page').object_list), 10)
