from django.test import TestCase, RequestFactory
from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponseRedirect

from uwsgiit_console import settings
from console.views import home, me_page, logout, domains, tags
from console.views_metrics import metrics, container, domain
from console.forms import NewDomainForm, TagForm
from console.models import NetworkRXContainerMetric, NetworkTXContainerMetric,\
    CPUContainerMetric, MemoryContainerMetric, IOReadContainerMetric,\
    IOWriteContainerMetric, QuotaContainerMetric, HitsDomainMetric,\
    NetworkRXDomainMetric, NetworkTXDomainMetric
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


class MetricsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        request_factory = RequestFactory()
        cls.request_get = request_factory.get('/metrics/', follow=True)
        cls.request_post = request_factory.post('/metrics/', follow=True)
        cls.request_get.session = {}
        cls.request_post.session = {}

    def test_metrics_name_resolves_to_metrics_url(self):
        url = reverse('metrics')
        self.assertEqual(url, '/metrics/')

    def test_metrics_url_resolves_to_metrics_view(self):
        resolver = resolve('/metrics/')
        self.assertEqual(resolver.func, metrics)

    def test_metrics_doesnt_allow_anonymous(self):
        response = metrics(self.request_get)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

        response = metrics(self.request_post)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(response.url, '/')

    def test_metrics_handles_logged_in_user(self):
        self.request_get.session = {
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD}
        response = metrics(self.request_get)
        self.request_get.session = {}
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Container IO read <span class="caret"></span>')


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
