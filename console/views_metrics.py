import json

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import CalendarForm
from .decorators import login_required
from .views import main_render


def stats_render(request, metrics, **kwargs):
    client = request.session.get('client')

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
    client = request.session.get('client')

    containers = client.containers(tags=[tag]).json()
    metrics = [kwargs['model'](container=c['uid']) for c in containers]

    return stats_render(request, metrics, **kwargs)


@login_required
def domain_metrics_per_tag(request, tag, **kwargs):
    client = request.session.get('client')

    domains = client.domains(tags=[tag]).json()
    metrics = [kwargs['model'](domain=d['id']) for d in domains]

    return stats_render(request, metrics, **kwargs)


@login_required
@ensure_csrf_cookie
def metric_detail(request):
    v_dict = {}
    # client = request.session.get('client')
    if request.GET:
        v_dict['dates'] = json.dumps(request.GET.getlist('date_list[]', None))
        v_dict['url'] = request.GET.get('metric_url', None)
        v_dict['metric_type'] = request.GET.get('metric_type', None)
        v_dict['subject'] = request.GET.get('subject', None)
    return main_render(request, 'metric_detail.html', v_dict)
