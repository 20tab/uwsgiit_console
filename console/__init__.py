VERSION = (0, 2)

__version__ = '.'.join((str(each) for each in VERSION[:3]))


def get_version():
    """
    Returns string with digit parts only as version.

    """
    return '.'.join((str(each) for each in VERSION[:2]))
