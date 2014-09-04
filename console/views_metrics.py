import json

from django.conf import settings
from django.http import HttpResponse

from uwsgiit.api import UwsgiItClient

from console.forms import CalendarForm
from console.decorators import login_required


def stats_render(request, metrics, **kwargs):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    time_unit = u'hour'
    metric_name = u'Invalid date'
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
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    containers = client.containers(tags=[tag]).json()
    metrics = [kwargs['model'](container=c['uid']) for c in containers]

    return stats_render(request, metrics, **kwargs)


@login_required
def domain_metrics_per_tag(request, tag, **kwargs):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    domains = client.domains(tags=[tag]).json()
    metrics = [kwargs['model'](domain=d['id']) for d in domains]

    return stats_render(request, metrics, **kwargs)
