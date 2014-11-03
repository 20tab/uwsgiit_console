from __future__ import unicode_literals, absolute_import
from datetime import datetime, timedelta
import re

from django import forms
from django.conf import settings
from django.utils.dates import MONTHS
from django.core.validators import validate_email
from django.core.urlresolvers import resolve, Resolver404

from uwsgiit.api import UwsgiItClient
from select2.widgets import SelectMultipleAutocomplete, SelectAutocomplete

from .models import UwsgiItApi


def email_list_validator(value):
    "Check if value consists only of valid emails."
    # Use the parent's handling of required fields, etc.
    for email in value:
        validate_email(email.strip())


class MultiEmailField(forms.CharField):

    default_validators = [email_list_validator]

    def to_python(self, value):
        "Normalize data to a list of strings."
        # Return an empty list if no input was given.
        if value in self.empty_values:
            return []
        return value.split(',')

    def clean(self, value):
        value = super(MultiEmailField, self).clean(value)
        return ','.join([email.strip() for email in value])


class TagsFormMixin(forms.Form):
    tags = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(),
        required=False)

    def __init__(self, *args, **kwargs):
        tag_choices = kwargs.pop('tag_choices')
        super(TagsFormMixin, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = tag_choices


class BootstrapForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for field in self.fields.keys():
            if not isinstance(self.fields[field].widget, (SelectAutocomplete, SelectMultipleAutocomplete)):
                self.fields[field].widget.attrs['class'] = 'form-control'


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
    email = MultiEmailField(label='Email', widget=forms.TextInput(
        attrs={'class': 'form-control col-xs-8'}), required=False)
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


class ContainerForm(TagsFormMixin):
    name = forms.CharField(label='Name', required=False)
    quota_threshold = forms.IntegerField(
        label='Quota Threshold', min_value=0, max_value=100)
    nofollow = forms.BooleanField(label='NoFollow', required=False)
    distro = forms.CharField(label='Distro', widget=forms.Select(choices=()))
    linked_to = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(),
        required=False)
    jid = forms.CharField(label='Jabber ID', required=False)
    jid_destinations = forms.CharField(
        label='Jabber Destinations', required=False)
    jid_secret = forms.CharField(
        label='Jabber Password', widget=forms.PasswordInput(), required=False)

    note = forms.CharField(
        widget=forms.Textarea(
            attrs={'cols': 50, 'rows': 3, 'class': 'form-control'}),
        required=False)

    def __init__(self, *args, **kwargs):
        distro_choices = kwargs.pop('distro_choices')
        linked_to_choices = kwargs.pop('linked_to_choices')
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['distro'].widget.choices = distro_choices
        self.fields['linked_to'].choices = linked_to_choices


class TagForm(forms.Form):
    name = forms.CharField(label='Name')


class DomainForm(TagsFormMixin):

    did = forms.IntegerField(widget=forms.HiddenInput, required=False)
    note = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'cols': 50, 'rows': 3, 'class': 'form-control'}))


class NewDomainForm(forms.Form):
    name = forms.CharField(
        label='Name', widget=forms.TextInput(attrs={'size': 70}))


class CalendarForm(forms.Form):
    year = forms.IntegerField()
    month = forms.ChoiceField(
        required=False,
        widget=SelectAutocomplete(plugin_options={"width": "200px"}),
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


class NewLoopboxForm(BootstrapForm):
    # container = forms.IntegerField(label='', widget=forms.HiddenInput())
    filename = forms.CharField(label='Filename')
    mountpoint = forms.CharField(label='Mount Point')
    readonly = forms.BooleanField(label='Readonly', required=False)


class LoopboxForm(TagsFormMixin):
    lid = forms.IntegerField(widget=forms.HiddenInput, required=False)


class AlarmForm(BootstrapForm):
    action_filter = forms.IntegerField(
        label='', widget=forms.HiddenInput(), initial=1)
    container = forms.IntegerField(required=False)
    vassal = forms.CharField(required=False)
    _class = forms.CharField(label='Class', required=False)
    color = forms.CharField(max_length=7, required=False)
    level = forms.ChoiceField(
        required=False,
        widget=SelectAutocomplete(plugin_options={"width": "100%"}),
        choices=(
            ('', ' '), (0, 'System'), (1, 'User'),
            (2, 'Exception'), (3, 'Traceback'), (4, 'Log')
        )
    )
    line = forms.IntegerField(min_value=0, required=False)
    filename = forms.CharField(required=False)
    func = forms.CharField(label='Function', required=False)

    def clean(self):
        cd = super(AlarmForm, self).clean()
        del cd['action_filter']
        return cd
