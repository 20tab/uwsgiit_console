from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from console.views import home, me_page, logout, domains, tags
from console.views_metrics import metrics_container, container,\
    domain, metrics_domain
from console.forms import NewDomainForm, TagForm
from console.models import IOReadContainerMetric, NetworkRXDomainMetric
#TODO TEST FORMS
#TODO TEST CONTAINERS


class HomeViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request = request_factory.get('/', follow=True)
        cls.request.session = {}
        cls.request_post = request_factory.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'action-login': 1})
        cls.request_post.session = {}

    def test_home_name_resolves_to_home_url(self):
        url = reverse('home')
        self.assertEqual(url, '/')

    def test_home_url_resolves_to_home_view(self):
        resolver = resolve('/')
        self.assertEqual(resolver.func, home)

    def test_home_returns_appropriate_html_respons_code(self):
        response = home(self.request)
        self.assertEqual(response.status_code, 200)

    def test_home_contains_right_html(self):
        response = home(self.request)
        self.assertContains(response, '<input name="action-login" type="hidden" value="1">')
        self.assertNotContains(response, 'href="#">Containers <span class="caret"></span></a>')

    def test_home_handles_logged_in_user(self):
        self.request.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD}
        response = home(self.request)
        self.request.session = {}
        self.assertContains(response, 'href="#">Containers <span class="caret"></span></a>')
        self.assertNotContains(response, '<input name="action-login" type="hidden" value="1">')

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

    def test_me_name_resolves_to_me_url(self):
        url = reverse('me')
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
            'password': settings.TEST_PASSWORD}
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

    def test_me_name_resolves_to_me_url(self):
        url = reverse('domains')
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
            'password': settings.TEST_PASSWORD}
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

    def test_me_name_resolves_to_me_url(self):
        url = reverse('tags')
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
            'password': settings.TEST_PASSWORD}
        response = tags(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, TagForm())


class Metrics_Domain_ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/domain/', follow=True)
        cls.request_post = request_factory.post('/metrics/domain/', follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}

    def test_metrics_name_resolves_to_metrics_url(self):
        url = reverse('metrics_domain')
        self.assertEqual(url, '/metrics/domain/')

    def test_metrics_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/')
        self.assertEqual(resolver.func, metrics_domain)

    def test_metrics_doesnt_allow_anonymous(self):
        response = metrics_domain(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = metrics_domain(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_metrics_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD}
        response = metrics_domain(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Domain Network RX <span class="caret"></span>')
        self.assertNotContains(response, 'Container IO read <span class="caret"></span>')


class Metrics_Container_ViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/container/', follow=True)
        cls.request_post = request_factory.post('/metrics/container/', follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}

    def test_metrics_name_resolves_to_metrics_url(self):
        url = reverse('metrics_container')
        self.assertEqual(url, '/metrics/container/')

    def test_metrics_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/')
        self.assertEqual(resolver.func, metrics_container)

    def test_metrics_doesnt_allow_anonymous(self):
        response = metrics_container(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = metrics_container(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_metrics_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD}
        response = metrics_container(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Container IO read <span class="caret"></span>')
        self.assertNotContains(response, 'Domain Network RX <span class="caret"></span>')


class ContainerMetricViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/container/io.read/1/', follow=True)
        cls.request_post = request_factory.post('/metrics/container/io.read/1/', follow=True,
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

    def test_IOReadContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('container_io_read', args=(1,))
        self.assertEqual(url, '/metrics/container/io.read/1/')

    def test_IOReadContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/io.read/1/')
        self.assertEqual(resolver.func, container)

    def test_IOWriteContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('container_io_write', args=(1,))
        self.assertEqual(url, '/metrics/container/io.write/1/')

    def test_IOWriteContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/io.write/1/')
        self.assertEqual(resolver.func, container)

    def test_NetworkRXContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('container_net_rx', args=(1,))
        self.assertEqual(url, '/metrics/container/net.rx/1/')

    def test_NetworkRXContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/net.rx/1/')
        self.assertEqual(resolver.func, container)

    def test_NetworkTXContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('container_net_tx', args=(1,))
        self.assertEqual(url, '/metrics/container/net.tx/1/')

    def test_NetworkTXContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/net.tx/1/')
        self.assertEqual(resolver.func, container)

    def test_CPUContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('container_cpu', args=(1,))
        self.assertEqual(url, '/metrics/container/cpu/1/')

    def test_CPUContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/cpu/1/')
        self.assertEqual(resolver.func, container)

    def test_MemoryContainerMetric_name_resolves_to_metrics_url(self):
        url = reverse('container_mem', args=(1,))
        self.assertEqual(url, '/metrics/container/mem/1/')

    def test_MemoryContainerMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/container/mem/1/')
        self.assertEqual(resolver.func, container)

    def test_container_view_doesnt_allows_anonymous(self):
        response = container(
            self.request_get, 1, **{'model': IOReadContainerMetric})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = container(
            self.request_post, 1, **{'model': IOReadContainerMetric})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_container_view_handles_logged_in_user(self):
        self.request_post.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
        }
        response = container(
            self.request_post, 1, **{'model': IOReadContainerMetric}
        )
        self.request_post.session = {}
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Container IO read <span class="caret"></span>')


class DomainMetricViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/domain/net.rx/1/1/', follow=True)
        cls.request_post = request_factory.post('/metrics/domain/net.rx/1/1/', follow=True,
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

    def test_NetworkRXDomainMetric_name_resolves_to_metrics_url(self):
        url = reverse('domain_net_rx', args=(1,))
        self.assertEqual(url, '/metrics/domain/net.rx/1/')

    def test_NetworkRXDomainMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/net.rx/1/')
        self.assertEqual(resolver.func, domain)

    def test_NetworkTXDomainMetric_name_resolves_to_metrics_url(self):
        url = reverse('domain_net_tx', args=(1,))
        self.assertEqual(url, '/metrics/domain/net.tx/1/')

    def test_NetworkTXDomainMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/net.tx/1/')
        self.assertEqual(resolver.func, domain)

    def test_HitsDomainMetric_name_resolves_to_metrics_url(self):
        url = reverse('domain_hits', args=(1,))
        self.assertEqual(url, '/metrics/domain/hits/1/')

    def test_HitsDomainMetric_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/domain/hits/1/')
        self.assertEqual(resolver.func, domain)

    def test_domain_view_doesnt_allows_anonymous(self):
        response = domain(
            self.request_get, 1, **{'model': NetworkRXDomainMetric})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = domain(
            self.request_post, 1, **{'model': NetworkRXDomainMetric})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_domain_view_handles_logged_in_user(self):
        self.request_post.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
        }
        response = domain(
            self.request_post, 1, **{'model': NetworkRXDomainMetric})
        self.request_post.session = {}
        self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Container IO read <span class="caret"></span>')


class LogoutViewTest(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/logout/', follow=True)
        cls.request_get.session = {}
        cls.request_post = request_factory.post('/logout/', follow=True)
        cls.request_post.session = {}

    def test_logout_name_resolves_to_logout_url(self):
        url = reverse('logout')
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
                'action-login': 1})
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
                'action-login': 1})
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/logout/', follow=True)
        self.assertRedirects(response, '/')
        response = self.client.get('/me/', follow=True)
        self.assertRedirects(response, '/')
