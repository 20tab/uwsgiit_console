uwsgiit_console
===============

A django app to simplify the use of uWSGI.it api with a few extras.

Real-time notification system for alarms!

You can take a look at the metrics of your containers, domains or all of the metrics of your domains and containers with the same tag!

![alt tag](https://github.com/20tab/uwsgiit_console/blob/master/demo/screens/screen.png)

INSTALLATION
============
## Installation

Use the following command:
```sh
    pip install uwsgiit-console
```

You should install this [uwsgi plugin](https://github.com/unbit/uwsgi-gif) too if you want to get colored gifs for real-time alarms.

## Configuration

Open settings.py and add select2 and console to your INSTALLED_APPS:

- settings.py

```py
INSTALLED_APPS = {
    ...,
    'select2',
    'console',
    ...
}
```

Add 'console.template_context.context_processors.console_context' to TEMPLATE_CONTEXT_PROCESSORS:

```py
TEMPLATE_CONTEXT_PROCESSORS = (
    ...,
    'console.template_context.context_processors.console_context',
    ...
)
```

In the end you can set a few variables:

```py
CONSOLE_TITLE = 'Whatever You Want'  #Default 'uWSGI.it Console'
CONSOLE_SUBTITLE = 'Whatever You Want'  #Default ''
DEFAULT_API_URL = 'https://whatever.you.want/'  #Default 'https://api.uwsgi.it/api/'
```

- urls.py

```py
urlpatterns = patterns('',
    ... ,
    (r'whatever/you/want', include('console.urls')),
    ...
)

```

- Static files

Run collectstatic command or map static directory.


- Add an uwsgi.it api in the database

In order to make it work you have to add one UwsgiItApi instance in the database containing the url you put in DEFAULT_API_URL.

- uwsgi-gif

If you installed uwsgi-gif you have to add those lines to your vassals:

```ini
[uwsgi]
plugin = gif
route = ^/foo_(\d+)_(\d+)_(\d+)\.gif$ gif:width=80,height=80,red=$1,green=$2,blue=$3
```


TEST
====
To launch test you should install tox (pip install tox) and you need to add a few variable into [console/tests/test_settings.py](https://github.com/20tab/uwsgiit_console/blob/master/console/tests/test_settings.py):

```py
    TEST_USER = 'USER_EXAMPLE'
    TEST_PASSWORD = 'PASSWORD_EXAMPLE'
    TEST_CONTAINER = '12345'
    TEST_DOMAIN = '123'
    TEST_TAG = 'TAG_EXAMPLE'
```

Now you can launch the tests with::

```sh
    ./run_tests
```

Now, since this project relies on third party API... you have to be patience, normally it takes around 1 minute.
