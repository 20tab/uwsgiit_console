from django.http import HttpResponseRedirect


def login_required(function):
    def wrap(request, *args, **kwargs):
        if request.session.get('client', False):
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
