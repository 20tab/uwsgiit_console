from __future__ import unicode_literals, absolute_import

from django.http import HttpResponseRedirect


def login_required(function):
    def wrap(request, *args, **kwargs):
        if (request.session.get('username', False) and
           request.session.get('password', False) and
           request.session.get('api_url', False)):
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap
