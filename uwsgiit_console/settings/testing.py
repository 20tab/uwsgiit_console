from .base import *

#Modify this to run tests
TEST_USER = 'USER_EXAMPLE'
TEST_PASSWORD = 'PASSWORD_EXAMPLE'
TEST_CONTAINER = '12345'
TEST_DOMAIN = '123'
TEST_TAG = 'TAG_EXAMPLE'
TEST_API_URL = 'https://api.uwsgi.it/api'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ':memory:',#os.path.dirname(__file__) + "/../dev.db",#'/path/example.db'. Path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',
    },
}
