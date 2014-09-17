"""
Django settings for uwsgiit_console project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os


gettext = lambda s: s

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Console configuration

CONSOLE_TITLE = 'uWSGI.it Console'
CONSOLE_SUBTITLE = '20tab srl'
DEFAULT_API_URL = 'https://api.uwsgi.it/api/'

######################

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'select2',
)

LOCAL_APPS = (
    'console',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

TEMPLATE_DIRS = (
    'templates',
)

MANAGERS = (("errors", "errors@email.com"),)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Or path to database file if using sqlite3.
        'NAME': 'uwsgiit_console.db',
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',  # Set to empty string for default. Not used with sqlite3.
    }
}


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j!7z%+(kog8tqv-%y7ga5a#0i+!mc_436p2u&i_v9uy1@!#^&t'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "console.template_context.context_processors.console_context",
)


SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

ROOT_URLCONF = 'uwsgiit_console.urls'

WSGI_APPLICATION = 'uwsgiit_console.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'static'))
MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'media'))
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

DEBUG = TEMPLATE_DEBUG = True
