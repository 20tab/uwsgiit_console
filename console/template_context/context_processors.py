from django.conf import settings


def console_context(request):
    context_extras = {}
    try:
        context_extras['CONSOLE_TITLE'] = settings.CONSOLE_TITLE
        context_extras['CONSOLE_SUBTITLE'] = settings.CONSOLE_SUBTITLE
    except:
        pass
    context_extras['JQUERY_LIB'] = settings.JQUERY_LIB
    return context_extras
