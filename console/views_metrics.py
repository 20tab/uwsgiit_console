from uwsgiit.api import UwsgiItClient
from django.conf import settings
from console.forms import CalendarForm
from console.decorators import login_required
from console.views import main_render
from console.models import DomainMetric
import uwsgiit
print uwsgiit


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


def stats_render(request, metric, **kwargs):
    get_metrics_without_parameters = True
    calendar = CalendarForm()
    metric_type = u'h'

    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    if request.POST:
        calendar = CalendarForm(request.POST)
        if calendar.is_valid():
            params = calendar.get_params()
            stats = metric.metrics(client, params)
            metric_type = calendar.metric_type()
            get_metrics_without_parameters = False

    if get_metrics_without_parameters:
        stats = metric.metrics(client)

    v_dict = {
        'stats': stats,
        'calendar': calendar,
        'metric_type': metric_type
    }

    if issubclass(metric.__class__, DomainMetric):
        v_dict['domains'] = client.domains().json()

    return main_render(request, 'metrics.html', v_dict, client)


@login_required
def container(request, container, **kwargs):
    metric = kwargs['model'](container=container)
    return stats_render(request, metric, **kwargs)


@login_required
def domain(request, domain, **kwargs):
    metric = kwargs['model'](domain=domain)
    return stats_render(request, metric, **kwargs)
