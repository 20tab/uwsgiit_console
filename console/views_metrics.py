from django.conf import settings
from uwsgiit.api import UwsgiItClient

from console.forms import CalendarForm
from console.decorators import login_required
from console.views import main_render


@login_required
def metrics_domain(request):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    domains = client.domains().json()
    return main_render(
        request, 'metrics_base.html', {'domains': domains}, client)


@login_required
def metrics_container(request):
    return main_render(request, 'metrics_base.html', {})


def stats_render(request, client, metric, v_dict={}):
    get_metrics_without_parameters = True
    calendar = CalendarForm()
    metric_type = u'h'

    if request.POST:
        calendar = CalendarForm(request.POST)
        if calendar.is_valid():
            params = calendar.get_params()
            stats = metric.metrics(client, params)
            metric_type = calendar.metric_type()
            get_metrics_without_parameters = False

    if get_metrics_without_parameters:
        stats = metric.metrics(client)

    v_dict['stats'] = stats
    v_dict['calendar'] = calendar
    v_dict['metric_type'] = metric_type

    return main_render(request, 'metrics.html', v_dict, client)


@login_required
def container(request, container, **kwargs):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    metric = kwargs['model'](container=container)
    return stats_render(request, client, metric)


@login_required
def domain(request, domain, **kwargs):
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    metric = kwargs['model'](domain=domain)
    v_dict = {'domains': client.domains().json()}
    return stats_render(request, client, metric, v_dict)
