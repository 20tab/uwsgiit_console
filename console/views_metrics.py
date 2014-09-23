from __future__ import unicode_literals, absolute_import
import json
import re

from django.http import HttpResponse
from django.forms import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie

from uwsgiit.api import UwsgiItClient as UC

from .forms import CalendarForm, MetricDetailForm
from .decorators import login_required
from .views import main_render


def stats_render(request, metrics, **kwargs):
    client = UC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    time_unit = 'hour'
    metric_name = 'Invalid date'
    stats = []
    if request.POST and request.is_ajax:
        calendar = CalendarForm(request.POST)
        if calendar.is_valid():
            params = calendar.get_params()
            metric_name = calendar.metric_name()
            time_unit = calendar.time_unit()
            stats = [metric.metrics(client, params) for metric in metrics]

    v_dict = {}
    v_dict['stats'] = stats
    v_dict['time_unit'] = time_unit
    v_dict['metric_name'] = metric_name
    v_dict['unit_of_measure'] = metrics[0].unit_of_measure
    v_dict['absolute_values'] = kwargs['absolute_values']
    v_dict['average'] = kwargs['average']
    return HttpResponse(json.dumps(v_dict))


@login_required
def container_metrics(request, container, **kwargs):
    metrics = [kwargs['model'](container=container)]
    return stats_render(request, metrics, **kwargs)


@login_required
def domain_metrics(request, domain, **kwargs):
    metrics = [kwargs['model'](domain=domain)]
    return stats_render(request, metrics, **kwargs)


@login_required
def container_metrics_per_tag(request, tag, **kwargs):
    client = UC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    containers = client.containers(tags=[tag]).json()
    metrics = [kwargs['model'](container=c['uid']) for c in containers]

    return stats_render(request, metrics, **kwargs)


@login_required
def domain_metrics_per_tag(request, tag, **kwargs):
    client = UC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    domains = client.domains(tags=[tag]).json()
    metrics = [kwargs['model'](domain=d['id']) for d in domains]

    return stats_render(request, metrics, **kwargs)


@login_required
@ensure_csrf_cookie
def metric_detail(request):
    v_dict = {}
    if request.GET and 'date_list[]' in request.GET:
        dates = request.GET.getlist('date_list[]')
        for date in dates:
            result = re.search(
                r'^year=\d{4}&month=\d{0,2}&day=\d{0,2}$', date)
            if result is None:
                msg = 'Invalid Date'
                raise ValidationError(msg)

        form = MetricDetailForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            v_dict['dates'] = json.dumps(dates)
            v_dict['url'] = cd['metric_url']
            v_dict['metric_type'] = cd['metric_type']
            v_dict['subject'] = cd['subject']
    return main_render(request, 'console/metric_detail.html', v_dict)
