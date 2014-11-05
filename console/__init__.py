from __future__ import unicode_literals


VERSION = (0, 3, 1)

__version__ = '.'.join((str(each) for each in VERSION[:4]))

DJANGO_VERSION = '==1.7'
SELECT2_VERSION = '==0.10'
UWSGIIT_VERSION = '>=0.9.0'
APPCONF_VERSION = '==0.6'


def get_version():
    """
    Returns string with digit parts only as version.

    """
    return '.'.join((str(each) for each in VERSION[:3]))
