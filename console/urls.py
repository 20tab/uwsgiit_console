from __future__ import unicode_literals, absolute_import

try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from .models import IOReadContainerMetric, IOWriteContainerMetric,\
    NetworkRXContainerMetric, NetworkTXContainerMetric, CPUContainerMetric,\
    MemoryContainerMetric, QuotaContainerMetric, NetworkRXDomainMetric,\
    NetworkTXDomainMetric, HitsDomainMetric


urlpatterns = patterns(
    'console.views',
    url(r'^$', 'home', name='console_home'),
    url(r'^me/$', 'me_page', name='console_me'),
    url(r'^logout/$', 'logout', name='console_logout'),
    url(r'^containers/(?P<id>\d+)$', 'containers', name='console_containers'),
    url(r'^domains/(?P<id>\d+)$', 'domain', name='console_domain'),
    url(r'^domains/$', 'domains', name='console_domains'),
    url(r'^tags/(?P<tag>.+)$', 'tag', name='console_tag'),
    url(r'^tags/$', 'tags', name='console_tags'),
    url(r'^alarms/$', 'alarms', name='console_alarms'),
    url(r'^latest_alarms/$', 'latest_alarms', name='console_latest_alarms'),
)

urlpatterns += patterns(
    'console.views_metrics',
    url(r'^metric/$', 'metric_detail', name='console_metric_detail'),
    url(r'^metrics/container/io.read/id/(\d+)/$', 'container_metrics', name='console_container_io_read',
        kwargs={'model': IOReadContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/io.write/id/(\d+)/$', 'container_metrics', name='console_container_io_write',
        kwargs={'model': IOWriteContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/net.rx/id/(\d+)/$', 'container_metrics', name='console_container_net_rx',
        kwargs={'model': NetworkRXContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/net.tx/id/(\d+)/$', 'container_metrics', name='console_container_net_tx',
        kwargs={'model': NetworkTXContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/cpu/id/(\d+)/$', 'container_metrics', name='console_container_cpu',
        kwargs={'model': CPUContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/mem/id/(\d+)/$', 'container_metrics', name='console_container_mem',
        kwargs={'model': MemoryContainerMetric, 'absolute_values': True, 'average': True}),
    url(r'^metrics/container/quota/id/(\d+)/$', 'container_metrics', name='console_container_quota',
        kwargs={'model': QuotaContainerMetric, 'absolute_values': True, 'average': False}),

    url(r'^metrics/container/io.read/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_io_read_per_tag',
        kwargs={'model': IOReadContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/io.write/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_io_write_per_tag',
        kwargs={'model': IOWriteContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/net.rx/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_net_rx_per_tag',
        kwargs={'model': NetworkRXContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/net.tx/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_net_tx_per_tag',
        kwargs={'model': NetworkTXContainerMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/container/cpu/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_cpu_per_tag',
        kwargs={'model': CPUContainerMetric, 'absolute_values': False, 'average': True}),
    url(r'^metrics/container/mem/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_mem_per_tag',
        kwargs={'model': MemoryContainerMetric, 'absolute_values': True, 'average': True}),
    url(r'^metrics/container/quota/tag/(.+)/$', 'container_metrics_per_tag', name='console_container_quota_per_tag',
        kwargs={'model': QuotaContainerMetric, 'absolute_values': True, 'average': False}),

    url(r'^metrics/domain/net.rx/id/(\d+)/$', 'domain_metrics', name='console_domain_net_rx',
        kwargs={'model': NetworkRXDomainMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/domain/net.tx/id/(\d+)/$', 'domain_metrics', name='console_domain_net_tx',
        kwargs={'model': NetworkTXDomainMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/domain/hits/id/(\d+)/$', 'domain_metrics', name='console_domain_hits',
        kwargs={'model': HitsDomainMetric, 'absolute_values': False, 'average': False}),

    url(r'^metrics/domain/net.rx/tag/(.+)/$', 'domain_metrics_per_tag', name='console_domain_net_rx_per_tag',
        kwargs={'model': NetworkRXDomainMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/domain/net.tx/tag/(.+)/$', 'domain_metrics_per_tag', name='console_domain_net_tx_per_tag',
        kwargs={'model': NetworkTXDomainMetric, 'absolute_values': False, 'average': False}),
    url(r'^metrics/domain/hits/tag/(.+)/$', 'domain_metrics_per_tag', name='console_domain_hits_per_tag',
        kwargs={'model': HitsDomainMetric, 'absolute_values': False, 'average': False}),
)
