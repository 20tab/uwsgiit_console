# from uwsgiit.api import UwsgiItClient
# from console.forms import LoginForm, MeForm
# from django.conf import settings
# from django.http import Http404, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from console.decorators import login_required
# import json
#
#
# @csrf_exempt
# @login_required
# def update_me(request):
#     if request.is_ajax():
#         client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)
#         form = MeForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             client.update_me({'company': cd['company'], 'password': cd['password']})
#             request.session['password'] = cd['password']
#         return HttpResponse(json.dumps({}), content_type="application/json")
#     raise Http404
