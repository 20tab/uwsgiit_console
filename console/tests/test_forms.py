from __future__ import unicode_literals
from pprint import pformat
from datetime import date, timedelta

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
            {'data': {'username': 'test', 'api_url': self.test_api.id, 'action_login': 1},
                'error': ('password', ['This field is required.'])},
            {'data': {'password': '1234', 'api_url': self.test_api.id, 'action_login': 1},
                'error': ('username', ['This field is required.'])},
            {'data': {'username': 'test', 'password': '1234', 'action_login': 1},
                'error': ('api_url', ['This field is required.'])},
            {'data': {'username': 'test', 'api_url': self.test_api.id},
                'error': ('action_login', ['This field is required.'])}
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                LoginForm,
                invalid_data['error'][0],
                invalid_data['error'][1],
                invalid_data['data'])

    def test_LoginForm_data_validation_for_valid_data(self):
        form = LoginForm({'username': settings.TEST_USER, 'password': settings.TEST_PASSWORD,
                         'api_url': self.test_api.id, 'action_login': 1})
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())

    def test_LoginForm_with_wrong_credentials_throws_error(self):
        form = LoginForm({'username': 'test', 'password': '1234', 'action_login': 1, 'api_url': self.test_api.id})
        self.assertFalse(form.is_valid())
        self.assertRaisesMessage(forms.ValidationError, 'Wrong username or password', form.clean)


class MeFormTests(FormTesterMixin, TestCase):

    def test_MeForm_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {'data': {'company': 'test', 're_password': '1234'},
                'error': ('password', ['This field is required.'])},
            {'data': {'password': '1234', 're_password': '1234', 'vat': 1},
                'error': ('company', ['This field is required.'])},
            {'data': {'company': 'test', 'password': '1234', 'vat': 1},
                'error': ('re_password', ['This field is required.'])},
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                MeForm,
                invalid_data['error'][0],
                invalid_data['error'][1],
                invalid_data['data'])

    def test_MeForm_data_validation_for_valid_data(self):
        form = MeForm({'company': 'test', 'password': '1234',
                         're_password': '1234', 'vat': 1})
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())

    def test_MeForm_with_different_passwords_throws_error(self):
        invalid_data = {
            'data': {'company': 'test', 're_password': '1234', 'password': '123'},
            'error': ('re_password', ['Passwords do not match'])}

        self.assertFormError(
            MeForm,
            invalid_data['error'][0],
            invalid_data['error'][1],
            invalid_data['data'])


class SSHFormTests(FormTesterMixin, TestCase):

    def test_SSHForm_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {'data': {}, 'error': ('key', ['This field is required.'])}
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                SSHForm,
                invalid_data['error'][0],
                invalid_data['error'][1],
                invalid_data['data'])

    def test_SSHForm_data_validation_for_valid_data(self):
        keys = [
            {'key': 'ssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
            {'key': '\n\tssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
            {'key': 'ssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local      \n'},

        ]
        for key in keys:
            form = SSHForm(key)
            self.assertTrue(form.is_valid())
            #this will throw an error if it doesn't clean correctly
            self.assertIsNotNone(form.clean())

    def test_SSHForm_with_wrong_ssh_throws_error(self):
        keys = [
            {'data': {'key': 'ssh-rsaZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
                'error': 'Insered value is not a ssh-rsa key'},
            {'data': {'key': 'ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo Test@Test.local'},
                'error': 'Insered value is not a ssh-rsa key'},
            {'data': {'key': 'ssh-rsa ZZZB3NzaC1yc2EZZZDAQABAFFBAQCui4hJItITzlRHo'},
                'error': 'Insered value is not a ssh-rsa key'},
            {'data': {'key': 'ssh-rsa ' + ('a' * 4096) + ' Test@Test.local'},
                'error': 'Key too long'}
        ]
        for key in keys:
            form = SSHForm(key['data'])
            self.assertFalse(form.is_valid())
            self.assertRaisesMessage(forms.ValidationError, key['error'], form.clean)


class ContainerFormTests(TestCase):

    def test_ContainerForm_data_validation_for_valid_data(self):
        form = ContainerForm({'tags': ['1'], 'linked_to': ['1'], 'distro': ['1'], 'quota_threshold': 90}, distro_choices=((1, 1), (2, 2)), tag_choices=((1, 1), (2, 2)), linked_to_choices=((1, 1), (2, 2)))
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())


class DomainFormTests(TestCase):

    def test_DomainForm_data_validation_for_valid_data(self):
        form = DomainForm({'did': 267, 'tags': [1]}, tag_choices=((1, 1), (2, 2)))
        self.assertTrue(form.is_valid())
        #this will throw an error if it doesn't clean correctly
        self.assertIsNotNone(form.clean())


class CalendarFormTests(FormTesterMixin, TestCase):

    @classmethod
    def setUpClass(cls):
        cls.today = date.today()

    def test_CalendarForm_data_validation_for_invalid_data(self):
        invalid_data_list = [
            {'data': {'year': 2014, 'day': 12},
                'error': ('month', ['Month is required.'])},
            {'data': {'month': 1},
                'error': ('year', ['This field is required.'])},
            {'data': {'month': 1, 'day': 12},
                'error': ('year', ['This field is required.'])},
            {'data': {'day': 12},
                'error': ('year', ['This field is required.'])},
        ]

        for invalid_data in invalid_data_list:
            self.assertFormError(
                CalendarForm,
                invalid_data['error'][0],
                invalid_data['error'][1],
                invalid_data['data'])

    def test_CalendarForm_data_validation_for_valid_data(self):
        valid_data_list = [
            {'year': self.today.year},
            {'year': self.today.year, 'month': self.today.month},
            {'year': self.today.year, 'month': self.today.month, 'day': self.today.day},
        ]
        for valid_data in valid_data_list:
            form = CalendarForm(valid_data)
            self.assertTrue(form.is_valid())
            #this will throw an error if it doesn't clean correctly
            self.assertIsNotNone(form.clean())

    def test_CalendarForm_time_unit_returns_right_value(self):
        valid_data_list = [
            {'data': {'year': self.today.year}, 'time_unit': 'month'},
            {'data': {'year': self.today.year, 'month': self.today.month}, 'time_unit': 'day'},
            {'data': {'year': self.today.year, 'month': self.today.month, 'day': self.today.day}, 'time_unit': 'hour'},
        ]
        for valid_data in valid_data_list:
            form = CalendarForm(valid_data['data'])
            self.assertEqual(form.is_valid(), True)
            self.assertEqual(form.time_unit(), valid_data['time_unit'])

    def test_CalendarForm_is_in_future_fails_with_date_in_the_future(self):
        one_year_in_future = self.today + timedelta(365)
        tomorrow = self.today + timedelta(365)
        invalid_data_list = [
            {'year': one_year_in_future.year},
            {'year': one_year_in_future.year, 'month': one_year_in_future.month},
            {'year': one_year_in_future.year, 'month': one_year_in_future.month, 'day': one_year_in_future.day},
            {'year': tomorrow.year, 'month': tomorrow.month, 'day': tomorrow.day},
        ]

        for invalid_data in invalid_data_list:
            form = CalendarForm(invalid_data)
            self.assertFalse(form.is_valid())
            self.assertRaisesMessage(forms.ValidationError, 'Set a date in the past.', form.clean)

