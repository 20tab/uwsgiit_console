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
    url(r'^containers/(?P<id>\d+)$', 'containers', name='containers'),
    url(r'^domains/(?P<id>\d+)$', 'domain', name='domain'),
    url(r'^domains/$', 'domains', name='domains'),
    url(r'^tags/(?P<tag>\w+)$', 'tag', name='tag'),
    url(r'^tags/$', 'tags', name='tags'),
)

urlpatterns += patterns(
    'console.views_metrics',
    url(r'^metrics/container/io.read/(\d+)/$', 'container_metrics',
        kwargs={'model': IOReadContainerMetric}, name='container_io_read'),
    url(r'^metrics/container/io.write/(\d+)/$', 'container_metrics',
        kwargs={'model': IOWriteContainerMetric}, name='container_io_write'),
    url(r'^metrics/container/net.rx/(\d+)/$', 'container_metrics',
        kwargs={'model': NetworkRXContainerMetric}, name='container_net_rx'),
    url(r'^metrics/container/net.tx/(\d+)/$', 'container_metrics',
        kwargs={'model': NetworkTXContainerMetric}, name='container_net_tx'),
    url(r'^metrics/container/cpu/(\d+)/$', 'container_metrics',
        kwargs={'model': CPUContainerMetric}, name='container_cpu'),
    url(r'^metrics/container/mem/(\d+)/$', 'container_metrics',
        kwargs={'model': MemoryContainerMetric, 'absolute_values': True}, name='container_mem'),
    url(r'^metrics/container/quota/(\d+)/$', 'container_metrics',
        kwargs={'model': QuotaContainerMetric, 'absolute_values': True}, name='container_quota'),

    url(r'^metrics/domain/net.rx/(\d+)/$', 'domain_metrics',
        kwargs={'model': NetworkRXDomainMetric}, name='domain_net_rx'),
    url(r'^metrics/domain/net.tx/(\d+)/$', 'domain_metrics',
        kwargs={'model': NetworkTXDomainMetric}, name='domain_net_tx'),
    url(r'^metrics/domain/hits/(\d+)/$', 'domain_metrics',
        kwargs={'model': HitsDomainMetric}, name='domain_hits'),
)

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
