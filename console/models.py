from __future__ import unicode_literals, absolute_import
import json
from datetime import date

from django.db import models
from .utils import all_days_of, excluded_days
from . import conf


def date_from_params(params):

    year = date.today().year
    month = None
    day = None
    if 'year' not in params:
        params['year'] = year
    if 'month' in params:
        month = params['month']
    if 'day' in params:
        day = params['day']

    return params, year, month, day


class UwsgiItApi(models.Model):
    url = models.CharField(max_length=512, unique=True)
    name = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.url


class GenericMetric(models.Model):
    container = models.PositiveIntegerField()

    year = models.PositiveIntegerField(null=True)
    month = models.PositiveIntegerField(null=True)
    day = models.PositiveIntegerField(null=True)

    # this ia blob containing raw metrics
    json = models.TextField(null=True)

    def __unicode__(self):
        return '{year}-{month}-{day}'.format(
            year=self.year, month=self.month, day=self.day)

    class Meta:
        abstract = True

    @property
    def unit_of_measure(self):
        return 'bytes'


class ContainerMetric(GenericMetric):

    def metrics(self, client, params={}):
        if not params:  #Gets Today metrics
            return self.api_metrics(client, params)

        params, year, month, day = date_from_params(params)

        model = self.__class__

        if day and month:
            try:
                metric = model.objects.get(container=self.container, **params)
                result = json.loads(metric.json)
            except model.DoesNotExist:
                result = self.api_metrics(client, params)
                item = model(container=self.container, json=result, **params)
                if date(year, month, day) != date.today():
                    item.save()
            return result

        results = []
        to_save = []
        items = model.objects.filter(container=self.container, **params)
        for i in items:
            results.extend(json.loads(i.json))
        all_days = all_days_of(**params)
        dates_in_db = [date(d.year, d.month, d.day) for d in items]
        for d in excluded_days(all_days, dates_in_db):
            if not month:
                params['month'] = d.month
            params['day'] = d.day
            result = self.api_metrics(client, params)
            item = model(container=self.container, json=result, **params)
            if date(params['year'], params['month'], params['day']) != date.today():
                to_save.append(item)
            results.extend(result)
        model.objects.bulk_create(to_save)
        return results

    class Meta:
        abstract = True
        unique_together = ('container', 'year', 'month', 'day')


class DomainMetric(GenericMetric):
    domain = models.PositiveIntegerField()

    def metrics(self, client, params={}, container=None):
        if not params:  #Gets Today metrics
            results = []
            for elem in self.api_metrics(client, params):
                if container:
                    if elem['container'] == container:
                        return elem['metrics']
                else:
                    results.extend(elem['metrics'])
                return results

        res = []
        to_save = []

        params, year, month, day = date_from_params(params)

        query_params = params.copy()

        if container:
            query_params['container'] = container

        model = self.__class__

        results = model.objects.filter(domain=self.domain, **query_params)

        for result in results:
            res.extend(json.loads(result.json))

        if day and month:
            if not results.exists():
                results = self.api_metrics(client, params)
                for elem in results:
                    item = model(domain=self.domain,
                                 container=elem['container'],
                                 json=elem['metrics'],
                                 **params)
                    if date(params['year'], params['month'], params['day']) != date.today():
                        to_save.append(item)
                    if not container or container == item.container:
                        res.extend(elem['metrics'])
        else:
            all_days = all_days_of(**params)
            dates_in_db = [date(d.year, d.month, d.day) for d in results]
            for d in excluded_days(all_days, dates_in_db):
                if not month:
                    params['month'] = d.month
                params['day'] = d.day
                results = self.api_metrics(client, params)
                for elem in results:
                    item = model(domain=self.domain,
                                 container=elem['container'],
                                 json=elem['metrics'],
                                 **params)
                    if date(params['year'], params['month'], params['day']) != date.today():
                        to_save.append(item)
                    if not container or container == item.container:
                            res.extend(elem['metrics'])
        model.objects.bulk_create(to_save)
        return res

    class Meta:
        abstract = True
        unique_together = ('domain', 'container', 'year', 'month', 'day')


# stores values from the tuntap router
class NetworkRXContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'net.rx', params).json()

    @property
    def verbose_name(self):
        return 'Network RX'


# stores values from the tuntap router
class NetworkTXContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'net.tx', params).json()

    @property
    def verbose_name(self):
        return 'Network TX'


# stores values from the container cgroup
class CPUContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'cpu', params).json()

    @property
    def unit_of_measure(self):
        return 'ticks'

    @property
    def verbose_name(self):
        return 'CPU Ticks'


# stores values from the container cgroup
class MemoryContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'mem', params).json()

    @property
    def verbose_name(self):
        return 'Memory'


# stores values from the container cgroup
class IOReadContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'io.read', params).json()

    @property
    def verbose_name(self):
        return 'IO Read'


# stores values from the container cgroup
class IOWriteContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'io.write', params).json()

    @property
    def verbose_name(self):
        return 'IO Write'


# uses perl Quota package
class QuotaContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_metric(self.container, 'quota', params).json()

    @property
    def verbose_name(self):
        return 'Used Disk Space'


class HitsDomainMetric(DomainMetric):
    def api_metrics(self, client, params):
        return client.domain_metric(self.domain, 'hits', params).json()

    @property
    def unit_of_measure(self):
        return 'hits'

    @property
    def verbose_name(self):
        return 'Hits'


class NetworkRXDomainMetric(DomainMetric):
    def api_metrics(self, client, params):
        return client.domain_metric(self.domain, 'net.rx', params).json()

    @property
    def verbose_name(self):
        return 'Network RX'


class NetworkTXDomainMetric(DomainMetric):
    def api_metrics(self, client, params):
        return client.domain_metric(self.domain, 'net.tx', params).json()

    @property
    def verbose_name(self):
        return 'Network TX'
