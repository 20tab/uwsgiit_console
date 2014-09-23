from __future__ import unicode_literals, absolute_import

from appconf import AppConf
from django.conf import settings


class ConsoleConf(AppConf):
    CONSOLE_TITLE = 'uWSGI.it Console'
    CONSOLE_SUBTITLE = ''
    DEFAULT_API_URL = 'https://api.uwsgi.it/api/'

    def configure_console_title(self, value):
        if not getattr(settings, 'CONSOLE_TITLE', None):
            self._meta.holder.CONSOLE_TITLE = value
            return value
        return getattr(settings, 'CONSOLE_TITLE')

    def configure_console_subtitle(self, value):
        if not getattr(settings, 'CONSOLE_SUBTITLE', None):
            self._meta.holder.CONSOLE_SUBTITLE = value
            return value
        return getattr(settings, 'CONSOLE_SUBTITLE')

    def configure_default_api_url(self, value):
        if not getattr(settings, 'DEFAULT_API_URL', None):
            self._meta.holder.DEFAULT_API_URL = value
            return value
        return getattr(settings, 'DEFAULT_API_URL')
