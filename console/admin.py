from django.contrib import admin
from console.models import *


class ContainerMetricAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'container', 'year', 'month', 'day')
    list_filter = ('year', 'month', 'day')


class DomainMetricAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'container', 'year', 'month', 'day')
    list_filter = ('year', 'month', 'day')


admin.site.register(NetworkRXContainerMetric, ContainerMetricAdmin)
admin.site.register(NetworkTXContainerMetric, ContainerMetricAdmin)
admin.site.register(CPUContainerMetric, ContainerMetricAdmin)
admin.site.register(MemoryContainerMetric, ContainerMetricAdmin)
admin.site.register(IOReadContainerMetric, ContainerMetricAdmin)
admin.site.register(IOWriteContainerMetric, ContainerMetricAdmin)
admin.site.register(QuotaContainerMetric, ContainerMetricAdmin)
admin.site.register(HitsDomainMetric, DomainMetricAdmin)
admin.site.register(NetworkRXDomainMetric, DomainMetricAdmin)
admin.site.register(NetworkTXDomainMetric, DomainMetricAdmin)