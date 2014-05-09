from django import forms
from select2.widgets import SelectMultipleAutocomplete


class LoginForm(forms.Form):
    username = forms.CharField(label=u'Username', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=u'Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


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
        attrs={'class': 'form-control col-xs-8'}))

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
    tags = forms.MultipleChoiceField(
        widget=SelectMultipleAutocomplete(plugin_options={"width": "300px"}),
        choices=(), required=False
    )


class NewDomainForm(forms.Form):
    name = forms.CharField(label=u'Name', widget=forms.TextInput(attrs={'size': 70}))