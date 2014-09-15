from pprint import pformat
from datetime import date

from django.test import TestCase
from django.conf import settings
from django import forms

from ..forms import LoginForm, MeForm, SSHForm, ContainerForm, DomainForm, CalendarForm
from ..models import UwsgiItApi


class FormTesterMixin():
    def assertFormError(self, form_cls, expected_error_name, expected_error_msg, data):
        test_form = form_cls(data=data)
        #if we get an error then the form should not be valid
        self.assertFalse(test_form.is_valid())
        self.assertEquals(
            test_form.errors[expected_error_name],
            expected_error_msg,
            msg="Expected {} : Actual {} : using data {}"
                .format(test_form.errors[expected_error_name],
                        expected_error_msg, pformat(data)))


class LoginFormTests(FormTesterMixin, TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_api = UwsgiItApi(
            url=settings.DEFAULT_API_URL,
            name='TEST API')
        cls.test_api.save()

    @classmethod
    def tearDownClass(cls):
        cls.test_api.delete()

    def test_LoginForm_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {u'data': {u'username': u'test', u'api_url': self.test_api.id, u'action_login': 1},
                u'error': (u'password', [u'This field is required.'])},
            {u'data': {u'password': u'1234', u'api_url': self.test_api.id, u'action_login': 1},
                u'error': (u'username', [u'This field is required.'])},
            {u'data': {u'username': u'test', u'password': u'1234', u'action_login': 1},
                u'error': (u'api_url', [u'This field is required.'])},
            {u'data': {u'username': u'test', u'api_url': self.test_api.id},
                u'error': (u'action_login', [u'This field is required.'])}
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                LoginForm,
                invalid_data[u'error'][0],
                invalid_data[u'error'][1],
                invalid_data[u'data'])

    def test_LoginForm_data_validation_for_valid_data(self):
        form = LoginForm({u'username': settings.TEST_USER, u'password': settings.TEST_PASSWORD,
                         u'api_url': self.test_api.id, u'action_login': 1})
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())

    def test_LoginForm_with_wrong_credentials_throws_error(self):
        form = LoginForm({u'username': u'test', u'password': u'1234', u'action_login': 1, u'api_url': self.test_api.id})
        self.assertFalse(form.is_valid())
        self.assertRaisesMessage(forms.ValidationError, u'Wrong username or password', form.clean)


class MeFormTests(FormTesterMixin, TestCase):

    def test_MeForm_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {u'data': {u'company': u'test', u're_password': u'1234'},
                u'error': (u'password', [u'This field is required.'])},
            {u'data': {u'password': u'1234', u're_password': u'1234', u'vat': 1},
                u'error': (u'company', [u'This field is required.'])},
            {u'data': {u'company': u'test', u'password': u'1234', u'vat': 1},
                u'error': (u're_password', [u'This field is required.'])},
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                MeForm,
                invalid_data[u'error'][0],
                invalid_data[u'error'][1],
                invalid_data[u'data'])

    def test_MeForm_data_validation_for_valid_data(self):
        form = MeForm({u'company': u'test', u'password': u'1234',
                         u're_password': u'1234', u'vat': 1})
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())

    def test_MeForm_with_different_passwords_throws_error(self):
        invalid_data = {
            u'data': {u'company': u'test', u're_password': u'1234', u'password': u'123'},
            u'error': (u're_password', [u'Passwords do not match'])}

        self.assertFormError(
            MeForm,
            invalid_data[u'error'][0],
            invalid_data[u'error'][1],
            invalid_data[u'data'])


class SSHFormTests(FormTesterMixin, TestCase):

    def test_SSHForm_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {u'data': {}, u'error': (u'key', [u'This field is required.'])}
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                SSHForm,
                invalid_data[u'error'][0],
                invalid_data[u'error'][1],
                invalid_data[u'data'])

    def test_SSHForm_data_validation_for_valid_data(self):
        keys = [
            {u'key': u'ssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
            {u'key': u'\n\tssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
            {u'key': u'ssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local      \n'},

        ]
        for key in keys:
            form = SSHForm(key)
            self.assertTrue(form.is_valid())
            #this will throw an error if it doesn't clean correctly
            self.assertIsNotNone(form.clean())

    def test_SSHForm_with_wrong_ssh_throws_error(self):
        keys = [
            {u'data': {u'key': u'ssh-rsaZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
                u'error': u'Insered value is not a ssh-rsa key'},
            {u'data': {u'key': u'ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
                u'error': u'Insered value is not a ssh-rsa key'},
            {u'data': {u'key': u'ssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo'},
                u'error': u'Insered value is not a ssh-rsa key'},
            {u'data': {u'key': u'ssh-rsa ' + (u'a' * 4096) + u' Test@Test.local'},
                u'error': u'Key too long'}
        ]
        for key in keys:
            form = SSHForm(key[u'data'])
            self.assertFalse(form.is_valid())
            self.assertRaisesMessage(forms.ValidationError, key[u'error'], form.clean)


class ContainerFormTests(TestCase):

    def test_ContainerForm_data_validation_for_valid_data(self):
        form = ContainerForm({u'tags': [u'1'], u'link_to': [u'1'], u'distro': [u'1']}, distro_choices=((1, 1), (2, 2)), tag_choices=((1, 1), (2, 2)), link_to_choices=((1, 1), (2, 2)))
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())


class DomainFormTests(TestCase):

    def test_DomainForm_data_validation_for_valid_data(self):
        form = DomainForm({u'did': 267, u'tags': [1]}, tag_choices=((1, 1), (2, 2)))
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())


# class CalendarFormTests(FormTesterMixin, TestCase):

#     @classmethod
#     def setUpClass(cls):
#         cls.today = date.today()

#     def test_CalendarForm_data_validation_for_invalid_data(self):
#         invalid_data_list = [
#             {u'data': {u'month': 1, u'day': 12},
#                 u'error': (u'year', [u'This field is required.'])}
#         ]

#         for invalid_data in invalid_data_list:
#             self.assertFormError(
#                 CalendarForm,
#                 invalid_data[u'error'][0],
#                 invalid_data[u'error'][1],
#                 invalid_data[u'data'])

#     def test_CalendarForm_data_validation_for_valid_data(self):
#         form = CalendarForm({u'year': self.today.year, u'month': self.today.month, u'day': self.today.day})
#         self.assertTrue(form.is_valid())
#         #this will throw an error if it doesn't clean correctly
#         self.assertIsNotNone(form.clean())

#     def test_CalendarForm_time_unit_returns_right_value(self):
#         form = CalendarForm({u'year': self.today.year, u'month': self.today.month, u'day': self.today.day})
#         form.clean()
#         self.assertEqual(form.time_unit(), u'hour')

#         form = CalendarForm({u'year': self.today.year, u'month': self.today.month})
#         form.clean()
#         self.assertEqual(form.time_unit(), u'day')

#         form = CalendarForm({u'year': self.today.year})
#         form.clean()
#         self.assertEqual(form.time_unit(), u'month')

