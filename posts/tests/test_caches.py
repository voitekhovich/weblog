from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()

PAGE_INDEX = 'index'


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text post'
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_cache_index_page(self):

        response = self.client.get(reverse(PAGE_INDEX))
        content_befor = response.content

        Post.objects.create(
            author=CacheTest.user,
            text='New test Text post'
        )

        response = self.client.get(reverse(PAGE_INDEX))
        content_after = response.content
        self.assertEqual(content_befor, content_after, 'Кеши не равны')

        cache.clear()

        response = self.client.get(reverse(PAGE_INDEX))
        content_after = response.content
        self.assertNotEqual(content_befor, content_after, 'Кеши равны')
