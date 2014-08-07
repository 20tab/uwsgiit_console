import random
from datetime import date

from django.test import TestCase
from django.conf import settings

from uwsgiit.api import UwsgiItClient

from console.utils import daterange
from console.models import ContainerMetric, DomainMetric,\
    NetworkRXContainerMetric, HitsDomainMetric


class MetricTesterMixin():

    @classmethod
    def createUwsgiItClient(cls):
        cls.client = UwsgiItClient(
            settings.TEST_USER,
            settings.TEST_PASSWORD,
            settings.CONSOLE_API)

    @classmethod
    def createTestMetric(cls, metric_class):
        parameters = {'container': 1}

        if issubclass(metric_class, ContainerMetric):
            pass
        elif issubclass(metric_class, DomainMetric):
            parameters['domain'] = 1
        else:
            raise TypeError('Cannot handle {class_name} class'.format(
                class_name=metric_class.__name__))

        start = date(2010, 01, 01)
        end = date(2010, 12, 31)

        cls.test_metrics = []

        for day in daterange(start, end):
            json = []
            for i in xrange(5):
                json.append([random.randint(1, 100), random.randint(1, 100)])
            parameters['day'] = day.day
            parameters['month'] = day.month
            parameters['year'] = day.year
            parameters['json'] = json
            test_metric = metric_class(**parameters)
            test_metric.save()
            cls.test_metrics.append(test_metric)


class ContainerMetricTests(MetricTesterMixin, TestCase):

    @classmethod
    def setUpClass(cls):
        cls.createTestMetric(NetworkRXContainerMetric)
        cls.createUwsgiItClient()
        cls.today = date.today()

    def test_generic_metric_to_string_prints_date(self):
        self.assertEqual(str(self.test_metrics[0]), '2010-1-1')

    def test_metric_returns_right_json_for_specific_day_from_db(self):
        result = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2010, 'month': 1, 'day': 1})
        self.assertEqual(len(result), len(self.test_metrics[0].json))
        self.assertEqual(sorted(result), sorted(self.test_metrics[0].json))

    def test_metric_returns_right_json_for_specific_month_from_db(self):
        results = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2010, 'month': 2})
        january_metrics = []
        [january_metrics.extend(el.json) for el in self.test_metrics[31:59]]
        self.assertEqual(len(results), len(january_metrics))
        self.assertEqual(sorted(results), sorted(january_metrics))

    def test_metric_returns_right_json_for_specific_year_from_db(self):
        results = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2010})
        year_metrics = []
        [year_metrics.extend(el.json) for el in self.test_metrics]
        self.assertEqual(len(results), len(year_metrics))
        self.assertEqual(sorted(results), sorted(year_metrics))

    # def test_metric_returns_right_json_for_specific_day_from_api(self):
    #     print dir(self.client)
    #     self.client1 = UwsgiItClient(
    #         settings.TEST_USER,
    #         settings.TEST_PASSWORD,
    #         settings.CONSOLE_API)
    #     print(dir(self.client1))
    #     results = NetworkRXContainerMetric(container=1).metrics(
    #         self.client, params={
    #         'year': self.today.year,
    #         'month': self.today.month,
    #         'day': self.today.day})
