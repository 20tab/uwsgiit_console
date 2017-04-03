from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from console.forms import NewDomainForm, TagForm
from console.views import home, me_page, logout, domains, domain, tags,\
    tag, containers, alarms, latest_alarms
from console.views_metrics import container_metrics, domain_metrics,\
    container_metrics_per_tag, domain_metrics_per_tag
from console.models import IOReadContainerMetric, NetworkRXDomainMetric,\
    UwsgiItApi


class HomeViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

        request_factory = RequestFactory()
        cls.request = request_factory.get('/', follow=True)
        cls.request.session = {}
        cls.request_post = request_factory.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': cls.test_api.id,
            'action_login': 1})
        cls.request_post.session = {}

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_home_name_resolves_to_home_url(self):
        url = reverse('console_home')
        self.assertEqual(url, '/')

    def test_home_url_resolves_to_home_view(self):
        resolver = resolve('/')
        self.assertEqual(resolver.func, home)

    def test_home_returns_appropriate_html_respons_code(self):
        response = home(self.request)
        self.assertEqual(response.status_code, 200)

    def test_home_contains_right_html(self):
        response = home(self.request)
        self.assertContains(response, 'id="id_action_login" name="action_login"')
        self.assertNotContains(response, 'Latest Alarms')

    def test_home_handles_logged_in_user(self):
        self.request.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = home(self.request)
        self.request.session = {}
        self.assertContains(response, 'Latest Alarms')
        self.assertNotContains(response, 'id="id_action_login" name="action_login"')

    def test_home_view_login_redirects_to_me_html(self):
        response = home(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/me/')


class MeViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/me/', follow=True)
        cls.request_post = request_factory.post('/me/', follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_me_name_resolves_to_me_url(self):
        url = reverse('console_me')
        self.assertEqual(url, '/me/')

    def test_me_url_resolves_to_me_view(self):
        resolver = resolve('/me/')
        self.assertEqual(resolver.func, me_page)

    def test_me_doesnt_allow_anonymous(self):
        response = me_page(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = me_page(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_me_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = me_page(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<tr><th><label for="id_company">Company:')


class DomainsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/domains/', follow=True)
        cls.request_post = request_factory.post('/domains/', follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_me_name_resolves_to_me_url(self):
        url = reverse('console_domains')
        self.assertEqual(url, '/domains/')

    def test_domains_url_resolves_to_domains_view(self):
        resolver = resolve('/domains/')
        self.assertEqual(resolver.func, domains)

    def test_domains_doesnt_allow_anonymous(self):
        response = domains(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = domains(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_domains_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = domains(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, NewDomainForm())


class TagsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/tags/', follow=True)
        cls.request_post = request_factory.post('/tags/', follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_me_name_resolves_to_me_url(self):
        url = reverse('console_tags')
        self.assertEqual(url, '/tags/')

    def test_tags_url_resolves_to_tags_view(self):
        resolver = resolve('/tags/')
        self.assertEqual(resolver.func, tags)

    def test_tags_doesnt_allow_anonymous(self):
        response = tags(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = tags(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_tags_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = tags(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, TagForm())


class Tag_ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.url = '/tags/{}'.format(settings.TEST_TAG)
        cls.request_get = request_factory.get(cls.url, follow=True)
        cls.request_post = request_factory.post(cls.url, follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_tag_name_resolves_to_metrics_url(self):
        url = reverse('console_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, self.url)

    def test_tag_url_resolves_to_metrics_view(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func, tag)

    def test_tag_doesnt_allow_anonymous(self):
        response = tag(self.request_get, settings.TEST_TAG)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = tag(self.request_post, settings.TEST_TAG)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_tag_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = tag(self.request_get, settings.TEST_TAG)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<h3><b>{tag}</b> Tag</h3>'.format(tag=settings.TEST_TAG))


class Domain_ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.url = '/domains/{}'.format(settings.TEST_DOMAIN)
        cls.request_get = request_factory.get(cls.url, follow=True)
        cls.request_post = request_factory.post(cls.url, follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_domain_name_resolves_to_metrics_url(self):
        url = reverse('console_domain', args=(settings.TEST_DOMAIN,))
        self.assertEqual(url, self.url)

    def test_domain_url_resolves_to_metrics_view(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func, domain)

    def test_domain_doesnt_allow_anonymous(self):
        response = domain(self.request_get, settings.TEST_DOMAIN)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = domain(self.request_post, settings.TEST_DOMAIN)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_domain_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = domain(self.request_get, settings.TEST_DOMAIN)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td>{id}</td>'.format(id=settings.TEST_DOMAIN))


class Containers_ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.url = '/containers/{}'.format(settings.TEST_CONTAINER)
        cls.request_get = request_factory.get(cls.url, follow=True)
        cls.request_post = request_factory.post(cls.url, follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_containers_name_resolves_to_containers_url(self):
        url = reverse('console_containers', args=(settings.TEST_CONTAINER,))
        self.assertEqual(url, self.url)

    def test_containers_url_resolves_to_containers_view(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func, containers)

    def test_containers_doesnt_allow_anonymous(self):
        response = containers(self.request_get, settings.TEST_CONTAINER)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = containers(self.request_post, settings.TEST_CONTAINER)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_containers_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = containers(self.request_get, settings.TEST_CONTAINER)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '({id})</b>'.format(id=settings.TEST_CONTAINER))


class AlarmsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.url = '/alarms/'
        cls.request_get = request_factory.get(cls.url, follow=True)
        cls.request_post = request_factory.post(cls.url, follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_alarms_name_resolves_to_alarms_url(self):
        url = reverse('console_alarms')
        self.assertEqual(url, self.url)

    def test_alarms_url_resolves_to_alarms_view(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func, alarms)

    def test_alarms_doesnt_allow_anonymous(self):
        response = alarms(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = alarms(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_alarms_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = alarms(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form class="form-horizontal" role="form" method="POST">')


class Latest_alarmsViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.url = '/latest_alarms/'
        cls.request_get = request_factory.get(cls.url, follow=True)
        cls.request_post = request_factory.post(cls.url, follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_latest_alarms_name_resolves_to_latest_alarms_url(self):
        url = reverse('console_latest_alarms')
        self.assertEqual(url, self.url)

    def test_latest_alarms_url_resolves_to_latest_alarms_view(self):
        resolver = resolve(self.url)
        self.assertEqual(resolver.func, latest_alarms)

    def test_latest_alarms_doesnt_allow_anonymous(self):
        response = latest_alarms(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = latest_alarms(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_latest_alarms_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': settings.DEFAULT_API_URL}
        response = latest_alarms(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)


class ContainerMetricViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/container/io.read/id/1/', follow=True)
        cls.request_post = request_factory.post(
            '/metrics/container/io.read/id/1/', follow=True,
            data={'year': 2000, 'month': 1, 'day': 1})
        cls.request_get.session = {}
        cls.request_post.session = {}
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
        cls.test_metric = IOReadContainerMetric(
            container=1,
            year=2000,
            month=1,
            day=1,
            json=json
        )

        cls.test_metric.save()
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()
        cls.test_metric.delete()

    def test_IOReadContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_container_io_read', args=(1,))
        self.assertEqual(url, '/metrics/container/io.read/id/1/')

    def test_IOReadContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/io.read/id/1/')
        self.assertEqual(resolver.func, container_metrics)

    def test_IOWriteContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_container_io_write', args=(1,))
        self.assertEqual(url, '/metrics/container/io.write/id/1/')

    def test_IOWriteContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/io.write/id/1/')
        self.assertEqual(resolver.func, container_metrics)

    def test_NetworkRXContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_container_net_rx', args=(1,))
        self.assertEqual(url, '/metrics/container/net.rx/id/1/')

    def test_NetworkRXContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/net.rx/id/1/')
        self.assertEqual(resolver.func, container_metrics)

    def test_NetworkTXContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_container_net_tx', args=(1,))
        self.assertEqual(url, '/metrics/container/net.tx/id/1/')

    def test_NetworkTXContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/net.tx/id/1/')
        self.assertEqual(resolver.func, container_metrics)

    def test_CPUContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_container_cpu', args=(1,))
        self.assertEqual(url, '/metrics/container/cpu/id/1/')

    def test_CPUContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/cpu/id/1/')
        self.assertEqual(resolver.func, container_metrics)

    def test_MemoryContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_container_mem', args=(1,))
        self.assertEqual(url, '/metrics/container/mem/id/1/')

    def test_MemoryContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/mem/id/1/')
        self.assertEqual(resolver.func, container_metrics)

    def test_IOReadContainerMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_container_io_read_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/container/io.read/tag/{}/'.format(settings.TEST_TAG))

    def test_IOReadContainerMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/io.read/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, container_metrics_per_tag)

    def test_IOWriteContainerMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_container_io_write_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/container/io.write/tag/{}/'.format(settings.TEST_TAG))

    def test_IOWriteContainerMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/io.write/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, container_metrics_per_tag)

    def test_NetworkRXContainerMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_container_net_rx_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/container/net.rx/tag/{}/'.format(settings.TEST_TAG))

    def test_NetworkRXContainerMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/net.rx/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, container_metrics_per_tag)

    def test_NetworkTXContainerMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_container_net_tx_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/container/net.tx/tag/{}/'.format(settings.TEST_TAG))

    def test_NetworkTXContainerMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/net.tx/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, container_metrics_per_tag)

    def test_CPUContainerMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_container_cpu_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/container/cpu/tag/{}/'.format(settings.TEST_TAG))

    def test_CPUContainerMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/cpu/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, container_metrics_per_tag)

    def test_MemoryContainerMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_container_mem_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/container/mem/tag/{}/'.format(settings.TEST_TAG))

    def test_MemoryContainerMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/mem/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, container_metrics_per_tag)

    def test_container_view_doesnt_allows_anonymous(self):
        response = container_metrics(
            self.request_get, 1, **{'model': IOReadContainerMetric, 'absolute_values': False, 'average': False})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = container_metrics(
            self.request_post, 1, **{'model': IOReadContainerMetric, 'absolute_values': False, 'average': False})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_container_view_handles_logged_in_user(self):
        self.request_post.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': self.test_api.id}
        response = container_metrics(
            self.request_post, 1, **{'model': IOReadContainerMetric, 'absolute_values': False, 'average': False})
        self.request_post.session = {}
        self.assertEqual(response.status_code, 200)


class DomainMetricViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/domain/net.rx/id/1/', follow=True)
        cls.request_post = request_factory.post(
            '/metrics/domain/net.rx/id/1/', follow=True,
            data={'year': 2000, 'month': 1, 'day': 1})
        cls.request_get.session = {}
        cls.request_post.session = {}
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

        cls.test_metric = NetworkRXDomainMetric(
            domain=1,
            container=1,
            year=2000,
            month=1,
            day=1,
            json=json
        )

        cls.test_metric.save()
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()
        cls.test_metric.delete()

    def test_NetworkRXDomainMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_domain_net_rx', args=(1,))
        self.assertEqual(url, '/metrics/domain/net.rx/id/1/')

    def test_NetworkRXDomainMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/net.rx/id/1/')
        self.assertEqual(resolver.func, domain_metrics)

    def test_NetworkTXDomainMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_domain_net_tx', args=(1,))
        self.assertEqual(url, '/metrics/domain/net.tx/id/1/')

    def test_NetworkTXDomainMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/net.tx/id/1/')
        self.assertEqual(resolver.func, domain_metrics)

    def test_HitsDomainMetric_name_resolves_to_metrics_url(self):
        url = reverse('console_domain_hits', args=(1,))
        self.assertEqual(url, '/metrics/domain/hits/id/1/')

    def test_HitsDomainMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/hits/id/1/')
        self.assertEqual(resolver.func, domain_metrics)

    def test_NetworkRXDomainMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_domain_net_rx_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/domain/net.rx/tag/{}/'.format(settings.TEST_TAG))

    def test_NetworkRXDomainMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/net.rx/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, domain_metrics_per_tag)

    def test_NetworkTXDomainMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_domain_net_tx_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/domain/net.tx/tag/{}/'.format(settings.TEST_TAG))

    def test_NetworkTXDomainMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/net.tx/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, domain_metrics_per_tag)

    def test_HitsDomainMetricPerTag_name_resolves_to_metrics_url(self):
        url = reverse('console_domain_hits_per_tag', args=(settings.TEST_TAG,))
        self.assertEqual(url, '/metrics/domain/hits/tag/{}/'.format(settings.TEST_TAG))

    def test_HitsDomainMetricPerTag_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/hits/tag/{}/'.format(settings.TEST_TAG))
        self.assertEqual(resolver.func, domain_metrics_per_tag)

    def test_domain_view_doesnt_allows_anonymous(self):
        response = domain_metrics(
            self.request_get, 1, **{'model': NetworkRXDomainMetric, 'absolute_values': False, 'average': False})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = domain_metrics(
            self.request_post, 1, **{'model': NetworkRXDomainMetric, 'absolute_values': False, 'average': False})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_domain_view_handles_logged_in_user(self):
        self.request_post.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': self.test_api.id}
        response = domain_metrics(
            self.request_post, 1, **{'model': NetworkRXDomainMetric, 'absolute_values': False, 'average': False})
        self.request_post.session = {}
        self.assertEqual(response.status_code, 200)


class LogoutViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/logout/', follow=True)
        cls.request_get.session = {}
        cls.request_post = request_factory.post('/logout/', follow=True)
        cls.request_post.session = {}

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_logout_name_resolves_to_logout_url(self):
        url = reverse('console_logout')
        self.assertEqual(url, '/logout/')

    def test_logout_url_resolves_to_logout_view(self):
        resolver = resolve('/logout/')
        self.assertEqual(resolver.func, logout)

    def test_logout_redirects_anonymous(self):
        response = tags(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = tags(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_logout_logs_out_logged_in_user(self):
        #login
        self.client.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': self.test_api.id,
            'action_login': 1})
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/logout/', follow=True)
        self.assertRedirects(response, '/')
        response = self.client.get('/me/', follow=True)
        self.assertRedirects(response, '/')

        #login
        self.client.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'api_url': self.test_api.id,
            'action_login': 1})
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/logout/', follow=True)
        self.assertRedirects(response, '/')
        response = self.client.get('/me/', follow=True)
        self.assertRedirects(response, '/')
