'''
Django settings for uwsgiit_console example project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
'''
import os


gettext = lambda s: s

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Console configuration

CONSOLE_TITLE = 'uWSGI.it Console'
CONSOLE_SUBTITLE = ''
DEFAULT_API_URL = 'https://api.uwsgi.it/api/'

TEST_USER = 'USER_EXAMPLE'
TEST_PASSWORD = 'PASSWORD_EXAMPLE'
TEST_CONTAINER = '12345'
TEST_DOMAIN = '123'
TEST_TAG = 'TAG_EXAMPLE'

######################

DEBUG = TEMPLATE_DEBUG = True

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
)

LOCAL_APPS = (
    'console',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

TEMPLATE_DIRS = (
    os.path.join(os.path.abspath(BASE_DIR), 'templates'),
)

MANAGERS = (('errors', 'errors@email.com'),)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
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
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'console.template_context.context_processors.console_context',
)


ROOT_URLCONF = 'console.urls'

WSGI_APPLICATION = 'uwsgiit_console.wsgi.demo.application'


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
