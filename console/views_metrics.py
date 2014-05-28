from uwsgiit.api import UwsgiItClient
from django.conf import settings
from console.forms import CalendarForm
from console.decorators import login_required
from console.views import main_render
import uwsgiit
print uwsgiit


def metrics(request):

    return main_render(request, 'metrics_base.html', {})


def stats_render(request, container_id, model, domain_id=None):
    client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)
    calendar = CalendarForm()

    m = model(container=container_id)
    if domain_id:
        m.domain = domain_id
    stats = m.metrics(client)
    metric_type = u'h'

    if request.POST:
        calendar = CalendarForm(request.POST)
        if calendar.is_valid():
            params = calendar.get_params()
            stats = m.metrics(client, params)
            metric_type = calendar.metric_type()

    return main_render(request, 'metrics.html', {
        'stats': stats,
        'calendar': calendar,
        'metric_type': metric_type
    })


@login_required
def container(request, container_id, model):
    return stats_render(request, container_id, model)


@login_required
def domain(request, domain_id, container_id, model):
    return stats_render(request, container_id, model, domain_id)
