from uwsgiit.api import UwsgiItClient
from django.conf import settings
from console.forms import CalendarForm
from console.decorators import login_required
from console.views import main_render
import uwsgiit
print uwsgiit


@login_required
def metrics(request):
    return main_render(request, 'metrics_base.html', {})


def stats_render(request, container_id, domain_id=None, **kwargs):
    get_metrics_without_parameters = True
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    calendar = CalendarForm()
    m = kwargs['model'](container=container_id)
    if domain_id:
        m.domain = domain_id
    metric_type = u'h'
    if request.POST:
        calendar = CalendarForm(request.POST)
        if calendar.is_valid():
            params = calendar.get_params()
            stats = m.metrics(client, params)
            metric_type = calendar.metric_type()
            get_metrics_without_parameters = False
    
    if get_metrics_without_parameters:
        stats = m.metrics(client)

    return main_render(request, 'metrics.html', {
        'stats': stats,
        'calendar': calendar,
        'metric_type': metric_type
    })


@login_required
def container(request, container_id, **kwargs):
    return stats_render(request, container_id, **kwargs)


@login_required
def domain(request, domain_id, container_id, **kwargs):
    return stats_render(request, container_id, domain_id, **kwargs)
