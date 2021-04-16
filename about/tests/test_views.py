from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:<name>, доступен."""
        reverse_pages_name = [reverse('about:author'), reverse('about:tech')]
        for reverse_page in reverse_pages_name:
            with self.subTest(reverse_page=reverse_page):
                request = self.guest_client.get(reverse_page)
                self.assertEqual(request.status_code, 200)

    def test_about_pages_uses_correct_template(self):
        """При запросе к about:<name> применяется шаблон about/<name>.html."""
        templates_pages_names = {
            'author.html': reverse('about:author'),
            'tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
