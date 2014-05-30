from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from console.models import *

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),

)
urlpatterns += patterns(
    'console.views',
    url(r'^$', 'home', name='home'),
    url(r'^me/$', 'me_page', name='me'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^containers/(?P<id>\d+)?$', 'containers', name='containers'),
    url(r'^domains/$', 'domains', name='domains'),
    url(r'^tags/$', 'tags', name='tags'),
)
urlpatterns += patterns(
    'console.views_metrics',
    url(r'^metrics/$', 'metrics'),
    url(r'^metrics/container.io.read/(\d+)$', 'container', {'model': IOReadContainerMetric}, name='container_io_read'),
    url(r'^metrics/container.io.write/(\d+)$', 'container', {'model': IOWriteContainerMetric},
        name='container_io_write'),
    url(r'^metrics/container.net.rx/(\d+)$', 'container', {'model': NetworkRXContainerMetric}, name='container_net_rx'),
    url(r'^metrics/container.net.tx/(\d+)$', 'container', {'model': NetworkTXContainerMetric}, name='container_net_tx'),
    url(r'^metrics/container.cpu/(\d+)$', 'container', {'model': CPUContainerMetric}, name='container_cpu'),
    url(r'^metrics/container.mem/(\d+)$', 'container',
        {'model': MemoryContainerMetric, 'absolute_values': True},
        name='container_mem'
    ),
    url(r'^metrics/container.quota/(\d+)$', 'container', {'model': QuotaContainerMetric}, name='container_quota'),

    url(r'^metrics/domain.net.rx/(?P<domain_id>\d+)/(?P<container_id>\d+)$', 'domain',
        {'model': NetworkRXDomainMetric}, name='domain_net_rx'),
    url(r'^metrics/domain.net.tx/(?P<domain_id>\d+)/(?P<container_id>\d+)$', 'domain',
        {'model': NetworkTXDomainMetric}, name='domain_net_tx'),
    url(r'^metrics/domain.hits/(?P<domain_id>\d+)/(?P<container_id>\d+)$', 'domain', {'model': HitsDomainMetric},
        name='domain_hits'),
)

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )