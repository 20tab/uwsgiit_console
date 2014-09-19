from django.conf import settings


CONSOLE_TITLE = getattr(settings, 'CONSOLE_TITLE', 'uWSGI.it Console')

CONSOLE_SUBTITLE = getattr(settings, 'CONSOLE_SUBTITLE', '20tab srl')

DEFAULT_API_URL = getattr(settings, 'DEFAULT_API_URL', 'https://api.uwsgi.it/api/')
