from uwsgiit.api import UwsgiItClient
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from console.decorators import login_required
from console.forms import LoginForm, MeForm, SSHForm, ContainerForm, TagForm,\
    DomainForm, NewDomainForm, CalendarForm


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')


def main_render(request, template, v_dict={}, client=None):
    login_form = LoginForm()
    if 'action-login' in request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            request.session['username'] = cd['username']
            request.session['password'] = cd['password']
            return HttpResponseRedirect('/me/')
    v_dict['login_form'] = login_form

    if (request.session.get('username', False) and
       request.session.get('password', False)):
        if client is None:
            client = UwsgiItClient(
                request.session.get('username'),
                request.session.get('password'),
                settings.CONSOLE_API)

        v_dict['containers'] = sorted(client.containers().json(), key=lambda k: k['name'])
        v_dict['login_form'] = None

    return render_to_response(template, v_dict, context_instance=RequestContext(request))


def home(request):
    return main_render(request, 'index.html', {})


@login_required
def me_page(request):

    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    me = client.me().json()
    v_dict = {'me': me}
    me_form = MeForm(initial={'company': me['company'],
                              'password': request.session.get('password'),
                              're_password': request.session.get('password'),
                              'vat': me['vat']})
    if request.POST:
        me_form = MeForm(request.POST)
        if me_form.is_valid():
            cd = me_form.cleaned_data
            client.update_me({'company': cd['company'],
                              'password': cd['password'],
                              'vat': cd['vat']})
            request.session['password'] = cd['password']

    v_dict['me_form'] = me_form
    v_dict['distros'] = client.distros().json()

    return main_render(request, 'me.html', v_dict, client)


@login_required
def containers(request, id):
    res = {}
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    if id:
        container = client.container(id).json()
        container_copy = container.copy()

        del container_copy['ssh_keys']
        del container_copy['distro']
        del container_copy['distro_name']
        del container_copy['tags']
        #del container_copy['linked_to']

        res['container_copy'] = container_copy
        res['container'] = container
        distros_list = client.distros().json()
        distros_list = sorted(distros_list, key=lambda distro: distro['id'], reverse=True)
        res['distros'] = distros_list
        distro_choices = [(x['id'], x['name']) for x in distros_list]

        tag_list = [(x['name'], x['name']) for x in client.list_tags().json()]

        containers_actual_link_to = [x for x in client.containers().json() if x['uid'] != int(id)]

        link_to = [(x['uid'], u"{} ({})".format(
            x['name'], x['uid'])) for x in containers_actual_link_to]
        containerform = ContainerForm(initial={'distro': "{}".format(container['distro'])},
                                      tags_choices=tag_list, link_to_choices=link_to)
        sshform = SSHForm()
        calendar = CalendarForm()

        active_panel = None
        if request.POST and 'action' in request.POST:
            action = request.POST['action']
            if action == 'update-container':
                containerform = ContainerForm(request.POST, tags_choices=tag_list, link_to_choices=link_to)
                if containerform.is_valid():
                    cd = containerform.cleaned_data
                    client.update_container(id, {'distro': cd['distro'],
                                                 'tags': cd['tags']})

                    list_link_to = [x['uid'] for x in containers_actual_link_to]

                    for link in cd['link_to']:
                        if link not in list_link_to:
                            client.update_container(id, {'link': link})
                    for link in list_link_to:
                        if unicode(link) not in cd['link_to']:
                            client.update_container(id, {'unlink': link})
            elif action == 'add-key':
                active_panel = 'ssh'
                sshform = SSHForm(request.POST)
                if sshform.is_valid():
                    cd = sshform.cleaned_data
                    if cd['key'] not in container['ssh_keys']:
                        container['ssh_keys'].append(cd['key'].strip())
                        response = client.container_set_keys(id, container['ssh_keys'])
                        if response.status_code == 200:
                            messages.success(request, 'New key successfully added')
                        else:
                            messages.error(request, 'An error occurred, please try again')
                        sshform = SSHForm()
                    else:
                        msg = 'Key {key} was already added to container {id}'.format(key=cd['key'], id=id)
                        messages.warning(request, msg)
            elif action == 'del-key':
                active_panel = 'ssh'
                sshform = SSHForm(request.POST)
                if sshform.is_valid():
                    cd = sshform.cleaned_data
                    cd['key'] = cd['key'].strip()
                    if cd['key'] in container['ssh_keys']:
                        container['ssh_keys'].remove(cd['key'])
                        client.container_set_keys(id, container['ssh_keys'])

        containerform.fields['distro'].widget.choices = distro_choices
        containerform.fields['tags'].initial = container['tags']
        containerform.fields['link_to'].initial = container['linked_to']
        res['containerform'] = containerform
        res['sshform'] = sshform
        res['calendar'] = calendar
        res['active_panel'] = active_panel
    return main_render(request, 'containers.html', res, client)


@login_required
def domains(request):
    res = {}
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    new_domain = NewDomainForm()
    calendar = CalendarForm()

    tags_list = [('', '')] + [(x['name'], x['name']) for x in client.list_tags().json()]

    if request.POST:
        if 'name' in request.POST:
            new_domain = NewDomainForm(request.POST)
            if new_domain.is_valid():
                name = new_domain.cleaned_data['name']
                client.add_domain(name)
                new_domain = NewDomainForm()
        else:
            domain_form = DomainForm(data=request.POST, choices=tags_list)
            if domain_form.is_valid():
                cd = domain_form.cleaned_data
                did = cd['did']
                tags_post = []
                if u'{}-tags'.format(did) in request.POST:
                    tags_post = request.POST.getlist(u'{}-tags'.format(did))
                client.update_domain(did, {'tags': tags_post})
    if 'del' in request.GET:
        name = request.GET['del']
        client.delete_domain(name)

    doms = []
    for d in client.domains().json():
        name = d['name']
        if len(name.split('.')) > 2:
            name = "{}.{}".format(name.split('.')[-2], name.split('.')[-1])
        d['key_name'] = name
        doms.append(d)

    doms = sorted(doms, key=lambda k: k['name'])
    doms = sorted(doms, key=lambda k: k['key_name'])
    domains_list = []
    for d in doms:
        form = DomainForm(initial={'did': d['id'], 'tags': d['tags']}, prefix=d['id'], choices=tags_list)
        domains_list.append((d, form))

    res['domains'] = domains_list
    res['new_domain'] = new_domain
    res['calendar'] = calendar

    return main_render(request, 'domains.html', res, client)


@login_required
def domain(request, id):
    calendar = CalendarForm()
    res = {}
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    tags_list = [('', '')] + [(x['name'], x['name']) for x in client.list_tags().json()]

    if request.POST:
        if u'did' in request.POST:
            domain_form = DomainForm(data=request.POST, choices=tags_list)
            if domain_form.is_valid():
                cd = domain_form.cleaned_data
                params = {}
                if u'tags' in cd:
                    params[u'tags'] = cd[u'tags']
                if u'note' in cd:
                    params[u'note'] = cd[u'note']
                client.update_domain(id, params)
    elif u'del' in request.GET:
        name = request.GET['del']
        client.delete_domain(name)

    domain = client.domain(id).json()
    form = DomainForm(choices=tags_list, initial={
        'did': id, 'tags': domain['tags'], 'note': domain['note']})

    del domain['tags']
    del domain['note']

    res['calendar'] = calendar
    res['domain'] = domain
    res['domainform'] = form
    return main_render(request, 'domain.html', res, client)


@login_required
def tags(request):
    res = {}
    tagform = TagForm()
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)

    if request.POST:
        tagform = TagForm(request.POST)
        if tagform.is_valid():
            cd = tagform.cleaned_data
            client.create_tag(cd['name'])
            tagform = TagForm()
    elif request.GET and 'id' in request.GET:
        id = request.GET['id']
        client.delete_tag(id)

    res['tags'] = client.list_tags().json()
    res['tagform'] = tagform
    return main_render(request, 'tags.html', res, client)


@login_required
def tag(request, tag):
    res = {}
    client = UwsgiItClient(
        request.session.get('username'),
        request.session.get('password'),
        settings.CONSOLE_API)
    doms = client.domains(tags=[tag]).json()
    domains = []
    tags_list = [('', '')] + [(x['name'], x['name']) for x in client.list_tags().json()]

    if request.POST:
        if '{}-did' in request.POST:
            domain_form = DomainForm(request.POST, choices=tags_list)
            if domain_form.is_valid():
                cd = domain_form.cleaned_data
                did = cd['did']
                tags_post = []
                if u'{}-tags'.format(did) in request.POST:
                    tags_post = request.POST.getlist(u'{}-tags'.format(did))
                client.update_domain(did, {'tags': tags_post})
    elif 'del' in request.GET:
        name = request.GET['del']
        client.delete_domain(name)

    for d in doms:
        form = DomainForm(initial={'did': d['id'], 'tags': d['tags']}, prefix=d['id'], choices=tags_list)
        domains.append((d, form))
    res['tag'] = tag
    res['tagged_domains'] = domains
    res['tagged_containers'] = client.containers(tags=[tag]).json()
    return main_render(request, 'tag.html', res, client)
