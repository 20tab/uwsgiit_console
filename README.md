uwsgiit_console
===============


TEST
====
To launch test you need to add a few variable into [uwsgiit_console/settings/testing.py](https://github.com/20tab/uwsgiit_console/blob/master/uwsgiit_console/settings/testing.py):

```py
    TEST_USER = 'USER_EXAMPLE'
    TEST_PASSWORD = 'PASSWORD_EXAMPLE'
    TEST_CONTAINER = '12345'
    TEST_DOMAIN = '123'
    TEST_TAG = 'TAG_EXAMPLE'
    DEFAULT_API_URL = 'https://api.uwsgi.it/api/'
```

Obviously you can change DEFAULT_API_URL with every uwsgi.it API you want to test it with

Now you can launch the tests with::

    python manage.py test --settings=uwsgiit_console.settings.testing


Now, since this project relies on third party APIs... you have to be patience, normally it takes around 1 minute.
