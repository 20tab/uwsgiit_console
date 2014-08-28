import re
from datetime import datetime, timedelta

from django import forms
from django.conf import settings
from django.utils.dates import MONTHS

from uwsgiit.api import UwsgiItClient
from select2.widgets import SelectMultipleAutocomplete, SelectAutocomplete


class LoginForm(forms.Form):
    username = forms.CharField(label=u'Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=u'Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cd = super(LoginForm, self).clean()
        username = cd['username']
        password = cd['password']
        client = UwsgiItClient(username, password, settings.CONSOLE_API)
        me = client.me().json()
        if 'error' in me:
            raise forms.ValidationError(u'Username o password errate!')
        return cd


class MeForm(forms.Form):
    company = forms.CharField(label=u'Company', widget=forms.TextInput(
        attrs={'class': 'form-control col-xs-8'}))
    password = forms.CharField(label=u'Password',
                               widget=forms.PasswordInput(render_value=True,
                                                          attrs={'class': 'form-control'}))
    re_password = forms.CharField(label=u'Retype password',
                                  widget=forms.PasswordInput(render_value=True,
                                                             attrs={'class': 'form-control'}))
    vat = forms.CharField(label=u'Vat', widget=forms.TextInput(
        attrs={'class': 'form-control col-xs-8'}), required=False)

    def clean(self):
        cd = super(MeForm, self).clean()
        p1 = cd['password']
        p2 = cd['re_password']
        if p1 != p2:
            self._errors[u're_password'] = self.error_class([u'Le password inserite non coincidono'])
        return cd


class SSHForm(forms.Form):
    key = forms.CharField(label=u'ssh key', widget=forms.Textarea(
        attrs={'cols': 100, 'rows': 3, 'class': 'form-control'}))

    def clean(self):
        """Raise a ValidationError if the
           value is longer than 4096 or doesn't
           match an ssh-rsa regex
        """
        data = super(SSHForm, self).clean()
        key = data['key'].strip()
        if len(key) <= 4096:
            result = re.search(
                r'^ssh-rsa [^ \t\n\r]* [^ \t\n\r]*@*$', key)
            if result is None:
                msg = u'Insered value is not a ssh-rsa key'
                raise forms.ValidationError(msg)
        else:
            msg = u'Key too long'
            raise forms.ValidationError(msg)
        return data


class ContainerForm(forms.Form):
    distro = forms.CharField(label=u'Distro', widget=forms.Select(choices=()))
    tags = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(), required=False
    )
    link_to = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(), required=False
    )

    def __init__(self, *args, **kwargs):
        tags_choices = kwargs.pop('tags_choices')
        link_to_choices = kwargs.pop('link_to_choices')
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = tags_choices
        self.fields['link_to'].choices = link_to_choices


class TagForm(forms.Form):
    name = forms.CharField(label=u'Name')


class DomainForm(forms.Form):

    did = forms.IntegerField(widget=forms.HiddenInput, required=False)
    note = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'cols': 50, 'rows': 3, 'class': 'form-control'}))

    def __init__(self, choices=(), *args, **kwargs):
        super(DomainForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = forms.MultipleChoiceField(
            widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
            choices=choices, required=False)


class NewDomainForm(forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'size': 70}))


class CalendarForm(forms.Form):
    year = forms.IntegerField(required=False)
    month = forms.ChoiceField(required=False,
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

    def has_value(self, field):
        data = self.cleaned_data
        if field in data and data[field]:
            return True
        return False

    def get_params(self):
        res = {}
        data = self.cleaned_data
        if self.has_value(u'year'):
            res[u'year'] = data[u'year']
        if self.has_value(u'month'):
            res[u'month'] = int(data[u'month'])
        if self.has_value(u'day'):
            res[u'day'] = data[u'day']
        return res

    def metric_name(self):
        metric_name = ''
        data = self.cleaned_data
        if self.has_value(u'year'):
            metric_name = str(data[u'year'])
            if self.has_value(u'month'):
                metric_name = str(data[u'month']) + '-' + metric_name
                if self.has_value(u'day'):
                    metric_name = str(data[u'day']) + '-' + metric_name
        return metric_name

    def metric_type(self):
        if self.has_value(u'day'):
            return u'hour'
        elif self.has_value(u'month'):
            return u'day'
        return u'month'

    def is_in_the_future(self):
        data = self.get_params()
        today = datetime.today()
        if 'year' in data and data['year'] > today.year:
            return True
        if 'year' in data and data['year'] == today.year and 'month' in data and data['month'] > today.month:
            return True
        if 'year' in data and data['year'] == today.year and 'month' in data and data['month'] == today.month and \
                'day' in data and data['day'] > today.day:
            return True
        return False

    def clean(self):
        data = super(CalendarForm, self).clean()
        if self.has_value(u'day') and not self.has_value(u'month'):
            self._errors[u'month'] = self.error_class([u'Month is required'])
        if self.has_value(u'month') and not self.has_value(u'year'):
            self._errors[u'year'] = self.error_class([u'Year is required'])
        if self.is_in_the_future():
            raise forms.ValidationError(u'Set a date in the past not in future.')
        return data
