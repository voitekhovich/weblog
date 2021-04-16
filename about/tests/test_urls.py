from django.test import TestCase, Client


class AboutUrlsTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов приложения about."""
        tests_urls = ['/about/author/', '/about/tech/']
        for url in tests_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов приложения about."""
        templates_pages_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/',
        }
        for template, url in templates_pages_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
