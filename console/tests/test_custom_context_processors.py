from django.test import TestCase

from django.conf import settings


class ConsoleContextProcessorTests(TestCase):

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
