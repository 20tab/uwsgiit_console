import json
from calendar import monthrange
from datetime import date
from django.utils.dates import MONTHS
from django.db import models
from console.utils import all_days_of, exluded_days


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


class GenericMetric(models.Model):
    container = models.PositiveIntegerField()

    year = models.PositiveIntegerField(null=True)
    month = models.PositiveIntegerField(null=True)
    day = models.PositiveIntegerField(null=True)

    # this ia blob containing raw metrics
    json = models.TextField(null=True)

    def __unicode__(self):
        return "%s-%s-%s" % (self.year, self.month, self.day)

    class Meta:
        abstract = True


class ContainerMetric(GenericMetric):

    def metrics(self, client, params={}):
        if not params:
            return self.api_metrics(client, params)
        res = []
        to_save = []

        params, year, month, day = date_from_params(params)

        model = self.__class__

        if day and month:
            try:
                result = model.objects.get(container=self.container, **params)
                res.extend(json.loads(result.json))
            except model.DoesNotExist:
                result = self.api_metrics(client, params)
                item = model(container=self.container, json=result, **params)
                if date(year, month, day) != date.today():
                    to_save.append(item)
                res.extend(result)
        elif month:

            items = model.objects.filter(container=self.container, **params)
            for i in items:
                res.extend(json.loads(i.json))
            all_days = all_days_of(year, month)
            dates_in_db = [date(d.year, d.month, d.day) for d in items]
            for d in exluded_days(all_days, dates_in_db):
                params['day'] = d.day
                res.extend(self.metrics(client, params))
        else:
            for m in MONTHS.keys():
                params['month'] = m
                res.extend(self.metrics(client, params))
        model.objects.bulk_create(to_save)
        return res

    class Meta:
        abstract = True
        unique_together = ('container', 'year', 'month', 'day')


class DomainMetric(GenericMetric):
    domain = models.PositiveIntegerField()

    def metrics(self, client, params={}):
        if not params:
            for elem in self.api_metrics(client, params):
                if elem['container'] == int(self.container):
                    return elem['metrics']
        res = []
        to_save = []

        params, year, month, day = date_from_params(params)

        model = self.__class__

        if day and month:
            try:
                result = model.objects.get(domain=self.domain, container=self.container, **params)
                res.extend(json.loads(result.json))
            except model.DoesNotExist:
                result = self.api_metrics(client, params)
                for elem in result:
                    item = model(domain=self.domain, container=self.container, json=elem['metrics'], **params)
                    if date(year, month, day) != date.today():
                        to_save.append(item)
                    if int(self.container) == elem['container']:
                        res.extend(elem['metrics'])
        elif month:

            items = model.objects.filter(domain=self.domain, container=self.container, **params)
            for i in items:
                res.extend(json.loads(i.json))
            all_days = all_days_of(year, month)
            dates_in_db = [date(d.year, d.month, d.day) for d in items]
            for d in exluded_days(all_days, dates_in_db):
                params['day'] = d.day
                res.extend(self.metrics(client, params))
        else:
            for m in MONTHS.keys():
                params['month'] = m
                res.extend(self.metrics(client, params))
        model.objects.bulk_create(to_save)
        return res

    class Meta:
        abstract = True
        unique_together = ('domain', 'container', 'year', 'month', 'day')


# stores values from the tuntap router
class NetworkRXContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_net_rx(self.container, params).json()


# stores values from the tuntap router
class NetworkTXContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_net_tx(self.container, params).json()


# stores values from the container cgroup
class CPUContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_cpu(self.container, params).json()


# stores values from the container cgroup
class MemoryContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_mem(self.container, params).json()


# stores values from the container cgroup
class IOReadContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_io_read(self.container, params).json()


# stores values from the container cgroup
class IOWriteContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_io_write(self.container, params).json()


# uses perl Quota package
class QuotaContainerMetric(ContainerMetric):
    def api_metrics(self, client, params):
        return client.container_quota(self.container, params).json()


class HitsDomainMetric(DomainMetric):
    def api_metrics(self, client, params):
        return client.domain_hits(self.domain, params).json()


class NetworkRXDomainMetric(DomainMetric):
    def api_metrics(self, client, params):
        return client.domain_net_rx(self.domain, params).json()


class NetworkTXDomainMetric(DomainMetric):
    def api_metrics(self, client, params):
        return client.domain_net_tx(self.domain, params).json()
