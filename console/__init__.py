VERSION = (0, 2, 2)

__version__ = '.'.join((str(each) for each in VERSION[:4]))

DJANGO_VERSION = '==1.7'
SELECT2_VERSION = '==0.10'
UWSGIIT_VERSION = '==0.8.1'

def get_version():
    """
    Returns string with digit parts only as version.

    """
    return '.'.join((str(each) for each in VERSION[:3]))
