from django.test import TestCase
from django.core.urlresolvers import resolve, reverse

from uwsgiit_console import settings

from console.views import home, me_page, logout, domains, tags


#TODO TEST FORMS
#TODO TEST CONTAINERS


class ConsoleViewTests(TestCase):

    def test_home_view(self):
        url = reverse('home')
        self.assertEqual(url, '/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, home)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, settings.CONSOLE_TITLE)

    def test_home_view_login_redirects_to_me_html(self):
        response = self.client.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'action-login': 1})
        self.assertTemplateUsed(response, "me.html")

    def test_me_view_anonymous(self):
        url = reverse('me')
        self.assertEqual(url, '/me/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, me_page)

        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/')

    def test_me_view_loads(self):
        #login
        self.client.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'action-login': 1})
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'me.html')
        self.assertContains(response, '<h2>Available distributions</h2>')

    def test_domains_view_anonymous(self):
        url = reverse('domains')
        self.assertEqual(url, '/domains/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, domains)

        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/')

    def test_domains_view_loads(self):
        #login
        self.client.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'action-login': 1})
        response = self.client.get('/domains/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'domains.html')
        self.assertContains(response, '<th>TAGS</th>')

    def test_tags_view_anonymous(self):
        url = reverse('tags')
        self.assertEqual(url, '/tags/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, tags)

        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/')

    def test_tags_view_loads(self):
        #login
        self.client.post('/', follow=True, data={
            'username': settings.TEST_USER,
            'password': settings.TEST_PASSWORD,
            'action-login': 1})
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tags.html')
        self.assertContains(response, '<span class="glyphicon glyphicon-remove-circle"></span>')

    def test_logout(self):
        url = reverse('logout')
        self.assertEqual(url, '/logout/')
        resolver = resolve(url)
        self.assertEqual(resolver.func, logout)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/')
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/')

        #login
        self.client.post('/', follow=True, data={
                'username': settings.TEST_USER,
                'password': settings.TEST_PASSWORD,
                'action-login': 1})
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url, follow=True)
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

        response = self.client.post(url, follow=True)
        self.assertRedirects(response, '/')
        response = self.client.get('/me/', follow=True)
        self.assertRedirects(response, '/')


