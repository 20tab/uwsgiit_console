import json

from django.conf import settings
from django.http import HttpResponse

from uwsgiit.api import UwsgiItClient

from console.forms import CalendarForm
from console.decorators import login_required


def stats_render(request, client, metric, v_dict={}):
    get_metrics_without_parameters = True
    time_unit = u'hour'
    metric_name = u'Invalid date'
    if request.POST and request.is_ajax:
        calendar = CalendarForm(request.POST)
        if calendar.is_valid():
            params = calendar.get_params()
            metric_name = calendar.metric_name()
            stats = metric.metrics(client, params)
            time_unit = calendar.time_unit()
            get_metrics_without_parameters = False

    if get_metrics_without_parameters:
        stats = metric.metrics(client)

    v_dict['stats'] = stats
    v_dict['time_unit'] = time_unit
    v_dict['metric_name'] = metric_name
    v_dict['unit_of_measure'] = metric.unit_of_measure
    return HttpResponse(json.dumps(v_dict))


@login_required
def container_metrics(request, container, **kwargs):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    metric = kwargs['model'](container=container)
    v_dict = {'absolute_values': kwargs['absolute_values']}
    return stats_render(request, client, metric, v_dict)


@login_required
def domain_metrics(request, domain, **kwargs):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    metric = kwargs['model'](domain=domain)
    v_dict = {'absolute_values': kwargs['absolute_values'],
              'domains': client.domains().json()}
    return stats_render(request, client, metric, v_dict)
