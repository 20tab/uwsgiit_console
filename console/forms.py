from __future__ import unicode_literals, absolute_import
from datetime import datetime, timedelta
import re

from django import forms
from django.conf import settings
from django.utils.dates import MONTHS
from django.core.urlresolvers import resolve, Resolver404

from uwsgiit.api import UwsgiItClient
from select2.widgets import SelectMultipleAutocomplete, SelectAutocomplete

from .models import UwsgiItApi


class LoginForm(forms.Form):
    action_login = forms.IntegerField(
        label='', widget=forms.HiddenInput(), initial=1)
    username = forms.CharField(label='', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))
    api_url = forms.ModelChoiceField(
        label='Api url :', queryset=UwsgiItApi.objects.none())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['api_url'].queryset = UwsgiItApi.objects.all()
        self.fields['api_url'].initial = UwsgiItApi.objects.get(
            url=settings.DEFAULT_API_URL)

    def clean(self):
        cd = super(LoginForm, self).clean()
        if 'username' in cd and 'password' in cd and 'api_url' in cd:
            client = UwsgiItClient(
                cd['username'],
                cd['password'],
                cd['api_url'].url)

            me = client.me().json()
            if 'error' in me:
                raise forms.ValidationError('Wrong username or password')
        return cd


class MeForm(forms.Form):
    company = forms.CharField(label='Company', widget=forms.TextInput(
        attrs={'class': 'form-control col-xs-8'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control'}, render_value=True))
    re_password = forms.CharField(
        label='Retype password',
        widget=forms.PasswordInput(
            render_value=True, attrs={'class': 'form-control'}))
    vat = forms.CharField(label='Vat', widget=forms.TextInput(
        attrs={'class': 'form-control col-xs-8'}), required=False)

    def clean(self):
        cd = super(MeForm, self).clean()
        if 'password' in cd and 're_password' in cd:
            p1 = cd['password']
            p2 = cd['re_password']
            if p1 != p2:
                self._errors['re_password'] = self.error_class(
                    ['Passwords do not match'])
        return cd


class SSHForm(forms.Form):
    key = forms.CharField(label='ssh key', widget=forms.Textarea(
        attrs={'cols': 100, 'rows': 3, 'class': 'form-control'}))

    def clean(self):
        """Raise a ValidationError if the
           value is longer than 4096 or doesn't
           match an ssh-rsa regex
        """
        data = super(SSHForm, self).clean()
        if 'key' in data:
            key = data['key'].strip()
            if len(key) <= 4096:
                result = re.search(
                    r'^ssh-rsa [^ \t\n\r]* [^ \t\n\r]*@*$', key)
                if result is None:
                    msg = 'Insered value is not a ssh-rsa key'
                    raise forms.ValidationError(msg)
            else:
                msg = 'Key too long'
                raise forms.ValidationError(msg)
        return data


class ContainerForm(forms.Form):
    distro = forms.CharField(label='Distro', widget=forms.Select(choices=()))
    tags = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(),
        required=False)
    link_to = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(),
        required=False)
    note = forms.CharField(
        widget=forms.Textarea(
            attrs={'cols': 50, 'rows': 3, 'class': 'form-control'}),
        required=False)

    def __init__(self, *args, **kwargs):
        distro_choices = kwargs.pop('distro_choices')
        tag_choices = kwargs.pop('tag_choices')
        link_to_choices = kwargs.pop('link_to_choices')
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['distro'].widget.choices = distro_choices
        self.fields['tags'].choices = tag_choices
        self.fields['link_to'].choices = link_to_choices


class TagForm(forms.Form):
    name = forms.CharField(label='Name')


class DomainForm(forms.Form):

    did = forms.IntegerField(widget=forms.HiddenInput, required=False)
    note = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'cols': 50, 'rows': 3, 'class': 'form-control'}))
    tags = forms.MultipleChoiceField(
        choices=(), required=False,
        widget=SelectMultipleAutocomplete(
            plugin_options={"width": "300px"}))

    def __init__(self, *args, **kwargs):
        tag_choices = kwargs.pop('tag_choices')
        super(DomainForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = tag_choices


class NewDomainForm(forms.Form):
    name = forms.CharField(
        label='Name', widget=forms.TextInput(attrs={'size': 70}))


class CalendarForm(forms.Form):
    year = forms.IntegerField()
    month = forms.ChoiceField(
        required=False,
        widget=SelectAutocomplete(plugin_options={"width": "300px"}),
        choices=[('', '')] + [(k, v) for k, v in MONTHS.items()])
    day = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(CalendarForm, self).__init__(*args, **kwargs)
        today = datetime.today()
        yesterday = today - timedelta(1)
        self.fields['year'].initial = yesterday.year
        self.fields['month'].initial = yesterday.month
        self.fields['day'].initial = yesterday.day
        self.fields['day'].widget.attrs['min'] = 1

    def has_value(self, field):
        data = self.cleaned_data
        if field in data and data[field]:
            return True
        return False

    def get_params(self):
        res = {}
        data = self.cleaned_data
        if self.has_value('year'):
            res['year'] = data['year']
        if self.has_value('month'):
            res['month'] = int(data['month'])
        if self.has_value('day'):
            res['day'] = data['day']
        return res

    def metric_name(self):
        metric_name = ''
        data = self.cleaned_data
        if self.has_value('year'):
            metric_name = str(data['year'])
            if self.has_value('month'):
                metric_name = str(data['month']) + '-' + metric_name
                if self.has_value('day'):
                    metric_name = str(data['day']) + '-' + metric_name
        return metric_name

    def time_unit(self):
        if self.has_value('day'):
            return 'hour'
        elif self.has_value('month'):
            return 'day'
        return 'month'

    def is_in_the_future(self):
        data = self.get_params()
        today = datetime.today()
        if 'year' in data and data['year'] > today.year:
            return True
        if ('year' in data and data['year'] == today.year and
           'month' in data and data['month'] > today.month):
            return True
        if ('year' in data and data['year'] == today.year and
           'month' in data and data['month'] == today.month and
           'day' in data and data['day'] > today.day):
            return True
        return False

    def clean(self):
        data = super(CalendarForm, self).clean()
        if self.has_value('day') and not self.has_value('month'):
            self._errors['month'] = self.error_class(['Month is required.'])
        if self.is_in_the_future():
            raise forms.ValidationError('Set a date in the past.')
        return data


class MetricDetailForm(forms.Form):
    metric_url = forms.CharField()
    metric_type = forms.CharField()
    subject = forms.CharField()

    def clean(self):
        cd = super(MetricDetailForm, self).clean()
        if 'metric_url' in cd:
            try:
                resolve(cd['metric_url'])
            except Resolver404:
                raise forms.ValidationError('Invalid url')
        return cd
