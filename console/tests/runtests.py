import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'

import django
from django.conf import settings


django.setup()

from django.test.utils import get_runner

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, failfast=False)
failures = test_runner.run_tests(['console'])

if failures:
    sys.exit(failures)
