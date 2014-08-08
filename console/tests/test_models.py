import random
import json
from datetime import date, timedelta

from django.test import TestCase
from django.conf import settings

from uwsgiit.api import UwsgiItClient

from console.utils import daterange
from console.models import ContainerMetric, DomainMetric,\
    NetworkRXContainerMetric, NetworkRXDomainMetric


class MetricTesterMixin():

    @classmethod
    def istanceUwsgiItClient(cls):
        cls.client = UwsgiItClient(
            settings.TEST_USER,
            settings.TEST_PASSWORD,
            settings.CONSOLE_API)

    @classmethod
    def createTestMetrics(cls, metric_class):
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
        cls.createTestMetrics(NetworkRXContainerMetric)
        cls.today = date.today()
        cls.yesterday = cls.today - timedelta(1)
        cls.tomorrow = cls.today + timedelta(1)

    def test_generic_metric_to_string_prints_date(self):
        self.assertEqual(str(self.test_metrics[0]), '2010-1-1')

    def test_metrics_returns_right_json_for_specific_day_from_db(self):
        result = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2010, 'month': 1, 'day': 1})
        self.assertEqual(len(result), len(self.test_metrics[0].json))
        self.assertEqual(sorted(result), sorted(self.test_metrics[0].json))

    def test_metrics_returns_right_json_for_specific_month_from_db(self):
        results = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2010, 'month': 2})
        january_metrics = []
        [january_metrics.extend(el.json) for el in self.test_metrics[31:59]]
        self.assertEqual(len(results), len(january_metrics))
        self.assertEqual(sorted(results), sorted(january_metrics))

    def test_metrics_returns_right_json_for_specific_year_from_db(self):
        results = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2010})
        year_metrics = []
        [year_metrics.extend(el.json) for el in self.test_metrics]
        self.assertEqual(len(results), len(year_metrics))
        self.assertEqual(sorted(results), sorted(year_metrics))

    def test_metrics_does_not_save_current_day_in_db(self):
        client = UwsgiItClient(
            settings.TEST_USER,
            settings.TEST_PASSWORD,
            settings.CONSOLE_API)

        NetworkRXContainerMetric(container=settings.TEST_CONTAINER).metrics(
            client, params={
                'year': self.today.year,
                'month': self.today.month,
                'day': self.today.day})

        self.assertRaises(
            NetworkRXContainerMetric.DoesNotExist,
            NetworkRXContainerMetric.objects.get,
            **{'container': settings.TEST_CONTAINER,
               'year': self.yesterday.year,
               'month': self.yesterday.month,
               'day': self.yesterday.day})

    def test_metrics_returns_right_json_for_specific_day_from_api_and_saves_in_db(self):
        client = UwsgiItClient(
            settings.TEST_USER,
            settings.TEST_PASSWORD,
            settings.CONSOLE_API)

        results = NetworkRXContainerMetric(container=settings.TEST_CONTAINER).metrics(
            client, params={
                'year': self.yesterday.year,
                'month': self.yesterday.month,
                'day': self.yesterday.day})

        metric_from_db = NetworkRXContainerMetric.objects.get(
            container=settings.TEST_CONTAINER,
            year=self.yesterday.year,
            month=self.yesterday.month,
            day=self.yesterday.day)

        self.assertEqual(results, json.loads(metric_from_db.json))

    def test_metrics_does_not_return_metrics_from_future_asking_for_current_month(self):
        """Assumes that today is not the last day of month"""

        client = UwsgiItClient(
            settings.TEST_USER,
            settings.TEST_PASSWORD,
            settings.CONSOLE_API)

        NetworkRXContainerMetric(container=settings.TEST_CONTAINER).metrics(
            client, params={
                'year': self.today.year,
                'month': self.today.month})

        self.assertRaises(
            NetworkRXContainerMetric.DoesNotExist,
            NetworkRXContainerMetric.objects.get,
            **{'container': settings.TEST_CONTAINER,
               'year': self.tomorrow.year,
               'month': self.tomorrow.month,
               'day': self.tomorrow.day})

    def test_metrics_returns_presents_metrics_from_db_and_missing_metrics_from_api(self):
        """Assumes that today is not the first day of month"""

        client = UwsgiItClient(
            settings.TEST_USER,
            settings.TEST_PASSWORD,
            settings.CONSOLE_API)

        test_metric = NetworkRXContainerMetric(
            container=settings.TEST_CONTAINER,
            json=[[-1, -2], [-3, -4]],
            year=self.yesterday.year,
            month=self.yesterday.month,
            day=self.yesterday.day)
        test_metric.save()

        results = NetworkRXContainerMetric(container=settings.TEST_CONTAINER).metrics(
            client, params={
                'year': self.today.year,
                'month': self.today.month})

        self.assertIn(test_metric.json[0], results)
        self.assertIn(test_metric.json[1], results)


# class DomainMetricTests(MetricTesterMixin, TestCase):

#     @classmethod
#     def setUpClass(cls):
#         cls.createTestMetrics(NetworkRXDomainMetric)
#         cls.today = date.today()
#         cls.yesterday = cls.today - timedelta(1)
#         cls.tomorrow = cls.today + timedelta(1)

#     def test_generic_metric_to_string_prints_date(self):
#         self.assertEqual(str(self.test_metrics[0]), '2010-1-1')

#     def test_metrics_returns_right_json_for_specific_day_from_db(self):
#         result = NetworkRXDomainMetric(domain=1).metrics(
#             self.client, params={'year': 2010, 'month': 1, 'day': 1})
#         self.assertEqual(len(result), len(self.test_metrics[0].json))
#         self.assertEqual(sorted(result), sorted(self.test_metrics[0].json))

#     def test_metrics_returns_right_json_for_specific_month_from_db(self):
#         results = NetworkRXDomainMetric(domain=1).metrics(
#             self.client, params={'year': 2010, 'month': 2})
#         january_metrics = []
#         [january_metrics.extend(el.json) for el in self.test_metrics[31:59]]
#         self.assertEqual(len(results), len(january_metrics))
#         self.assertEqual(sorted(results), sorted(january_metrics))

#     def test_metrics_returns_right_json_for_specific_year_from_db(self):
#         results = NetworkRXDomainMetric(domain=1).metrics(
#             self.client, params={'year': 2010})
#         year_metrics = []
#         [year_metrics.extend(el.json) for el in self.test_metrics]
#         self.assertEqual(len(results), len(year_metrics))
#         self.assertEqual(sorted(results), sorted(year_metrics))

#     def test_metrics_does_not_save_current_day_in_db(self):
#         client = UwsgiItClient(
#             settings.TEST_USER,
#             settings.TEST_PASSWORD,
#             settings.CONSOLE_API)

#         NetworkRXDomainMetric(domain=settings.TEST_DOMAIN).metrics(
#             client, params={
#                 'year': self.today.year,
#                 'month': self.today.month,
#                 'day': self.today.day})

#         self.assertRaises(
#             NetworkRXDomainMetric.DoesNotExist,
#             NetworkRXDomainMetric.objects.get,
#             **{'domain': settings.TEST_DOMAIN,
#                'year': self.yesterday.year,
#                'month': self.yesterday.month,
#                'day': self.yesterday.day})

#     def test_metrics_returns_right_json_for_specific_day_from_api_and_saves_in_db(self):
#         client = UwsgiItClient(
#             settings.TEST_USER,
#             settings.TEST_PASSWORD,
#             settings.CONSOLE_API)

#         results = NetworkRXDomainMetric(domain=settings.TEST_DOMAIN).metrics(
#             client, params={
#                 'year': self.yesterday.year,
#                 'month': self.yesterday.month,
#                 'day': self.yesterday.day})

#         metric_from_db = NetworkRXDomainMetric.objects.get(
#             domain=settings.TEST_DOMAIN,
#             year=self.yesterday.year,
#             month=self.yesterday.month,
#             day=self.yesterday.day)

#         self.assertEqual(results, json.loads(metric_from_db.json))

#     def test_metrics_does_not_return_metrics_from_future_asking_for_current_month(self):
#         """Assumes that today is not the last day of month"""

#         client = UwsgiItClient(
#             settings.TEST_USER,
#             settings.TEST_PASSWORD,
#             settings.CONSOLE_API)

#         NetworkRXDomainMetric(domain=settings.TEST_DOMAIN).metrics(
#             client, params={
#                 'year': self.today.year,
#                 'month': self.today.month})

#         self.assertRaises(
#             NetworkRXDomainMetric.DoesNotExist,
#             NetworkRXDomainMetric.objects.get,
#             **{'domain': settings.TEST_DOMAIN,
#                'year': self.tomorrow.year,
#                'month': self.tomorrow.month,
#                'day': self.tomorrow.day})

#     def test_metrics_returns_presents_metrics_from_db_and_missing_metrics_from_api(self):
#         """Assumes that today is not the first day of month"""

#         client = UwsgiItClient(
#             settings.TEST_USER,
#             settings.TEST_PASSWORD,
#             settings.CONSOLE_API)

#         test_metric = NetworkRXDomainMetric(
#             domain=settings.TEST_DOMAIN,
#             json=[[-1, -2], [-3, -4]],
#             year=self.yesterday.year,
#             month=self.yesterday.month,
#             day=self.yesterday.day)
#         test_metric.save()

#         results = NetworkRXDomainMetric(domain=settings.TEST_DOMAIN).metrics(
#             client, params={
#                 'year': self.today.year,
#                 'month': self.today.month})

#         self.assertIn(test_metric.json[0], results)
#         self.assertIn(test_metric.json[1], results)
