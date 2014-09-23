from __future__ import unicode_literals, absolute_import

from django.conf import settings


def console_context(request):
    context_extras = {}
    try:
        context_extras['CONSOLE_TITLE'] = settings.CONSOLE_TITLE
        context_extras['CONSOLE_SUBTITLE'] = settings.CONSOLE_SUBTITLE
        context_extras['JQUERY_LIB'] = settings.JQUERY_LIBJQUERY_LIB
    except AttributeError:
        pass
    context_extras['path'] = request.get_full_path()
    return context_extras
