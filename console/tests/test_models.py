from django.test import TestCase
from django.conf import settings

from uwsgiit.api import UwsgiItClient

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
        json = [
            [1407103492, 12288], [1407103808, 12288], [1407104120, 12288],
            [1407104436, 12288], [1407104748, 12288], [1407105061, 12288],
            [1407105374, 12288], [1407105687, 12288], [1407105997, 12288],
            [1407106309, 12288], [1407106619, 12288], [1407106930, 12288],
            [1407107241, 12288], [1407107552, 12288], [1407107865, 12288],
            [1407108179, 12288], [1407108490, 12288], [1407108805, 12288],
            [1407109116, 12288], [1407109428, 12288], [1407109740, 12288],
            [1407110052, 12288], [1407110366, 12288], [1407110683, 12288],
            [1407110995, 12288], [1407111311, 12288], [1407111621, 12288],
            [1407111932, 12288], [1407112245, 12288], [1407112559, 12288],
            [1407112872, 12288], [1407113183, 12288], [1407113495, 12288],
            [1407113808, 12288], [1407114119, 12288], [1407114431, 12288],
            [1407114744, 12288], [1407115055, 12288], [1407115366, 12288],
            [1407115679, 12288], [1407115993, 12288], [1407116306, 12288],
            [1407116619, 12288], [1407116932, 12288], [1407117246, 12288],
            [1407117560, 12288], [1407117869, 12288], [1407118179, 12288],
            [1407118499, 12288], [1407118819, 12288], [1407119132, 12288],
            [1407119446, 12288], [1407119765, 12288], [1407120082, 12288],
            [1407120398, 12288], [1407120711, 12288], [1407121025, 12288],
            [1407121336, 12288], [1407121651, 12288], [1407121963, 12288],
            [1407122274, 12288], [1407122585, 12288], [1407122897, 12288],
            [1407123209, 12288], [1407123526, 12288], [1407123840, 12288],
            [1407124151, 12288], [1407124464, 12288], [1407124777, 12288],
        ]
        parameters = {
            'container': 1,
            'year': 2014,
            'month': 1,
            'day': 1,
            'json': json
        }
        if issubclass(metric_class, ContainerMetric):
            pass
        elif issubclass(metric_class, DomainMetric):
            #insert domain_id
            parameters['domain'] = 1
        else:
            raise TypeError('Cannot handle {class_name} class'.format(
                class_name=metric_class.__name__))

        cls.test_metric = metric_class(**parameters)
        cls.test_metric.save()


class ContainerMetricTests(MetricTesterMixin, TestCase):

    @classmethod
    def setUpClass(cls):
        cls.createTestMetric(NetworkRXContainerMetric)
        cls.createUwsgiItClient()

    def test_generic_metric_to_string_prints_date(self):
        self.assertEqual(str(self.test_metric), '2014-1-1')

    def test_metric_returns_right_json_specific_day(self):
        result = NetworkRXContainerMetric(container=1).metrics(
            self.client, params={'year': 2014, 'month': 1, 'day': 1})
        self.assertEqual(result, self.test_metric.json)

