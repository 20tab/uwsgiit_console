from django.test import TestCase
from django.conf import settings

from ..models import UwsgiItApi


class ConsoleContextProcessorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    def test_request_attributes(self):
        url = '/'
        response = self.client.get(url)
        try:
            self.assertEqual(
                settings.CONSOLE_TITLE, response.context['CONSOLE_TITLE'])
            self.assertEqual(
                settings.CONSOLE_SUBTITLE, response.context['CONSOLE_SUBTITLE'])
            self.assertEqual(
                settings.JQUERY_LIBJQUERY_LIB, response.context['JQUERY_LIB'])
        except AttributeError:
            pass
        self.assertEqual(response.context['path'], url)

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()
