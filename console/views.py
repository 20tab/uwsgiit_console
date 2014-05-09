from uwsgiit.api import UwsgiItClient
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponseRedirect
from console.forms import LoginForm, MeForm, SSHForm, ContainerForm, TagForm, DomainForm, NewDomainForm
from console.decorators import login_required


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')


def main_render(request, template, v_dict={}):
    v_dict['path'] = request.get_full_path()
    login_form = LoginForm()
    if request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            request.session['username'] = cd['username']
            request.session['password'] = cd['password']
            return HttpResponseRedirect('/me/')
    v_dict['login_form'] = login_form

    if request.session.get('username', False) and request.session.get('password', False):
        client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)

        v_dict['containers'] = client.containers().json()
        v_dict['login_form'] = None

    return render_to_response(template, v_dict, context_instance=RequestContext(request))


def home(request):
    return main_render(request, 'index.html', {})

@login_required
def me_page(request):
    client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)
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

    return main_render(request, 'me.html', v_dict)


@login_required
def containers(request, id):
    res = {}
    client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)
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
        res['distros'] = distros_list
        distro_choices = [(x['id'], x['name']) for x in distros_list]

        tag_list = [(x['name'], x['name']) for x in client.list_tags().json()]

        containers_actual_link_to = [x for x in client.containers().json() if x['uid'] != int(id)]

        link_to = [(x['uid'], u"{} ({})".format(
            x['name'], x['uid'])) for x in containers_actual_link_to]
        containerform = ContainerForm(initial={'distro': "{}".format(container['distro'])},
                                      tags_choices=tag_list, link_to_choices=link_to)
        sshform = SSHForm()

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
                        print link
                        if link not in list_link_to:
                            print "\n\nQUI"
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
                        client.container_set_keys(id, container['ssh_keys'])
                        sshform = SSHForm()
            elif action == 'del-key':
                active_panel = 'ssh'
                sshform = SSHForm(request.POST)
                if sshform.is_valid():
                    cd = sshform.cleaned_data
                    if cd['key'] in container['ssh_keys']:
                        container['ssh_keys'].remove(cd['key'])
                        client.container_set_keys(id, container['ssh_keys'])

        containerform.fields['distro'].widget.choices = distro_choices
        containerform.fields['tags'].initial = container['tags']
        containerform.fields['link_to'].initial = container['linked_to']
        res['containerform'] = containerform
        res['sshform'] = sshform

        res['active_panel'] = active_panel
    return main_render(request, 'containers.html', res)


@login_required
def domains(request):
    res = {}
    client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)
    new_domain = NewDomainForm()

    if request.POST:
        if 'name' in request.POST:
            new_domain = NewDomainForm(request.POST)
            if new_domain.is_valid():
                name = new_domain.cleaned_data['name']
                client.add_domain(name)
                new_domain = NewDomainForm()
        else:
            domain_form = DomainForm(request.POST)
            if domain_form.is_valid():
                cd = domain_form.cleaned_data
                did = cd['did']
                tags_post = []
                if u'{}-tags'.format(did) in request.POST:
                    tags_post = request.POST.getlist(u'{}-tags'.format(did))
                client.update_domain(did,{'tags': tags_post})
    if 'del' in request.GET:
        name = request.GET['del']
        client.delete_domain(name)

    doms = client.domains().json()

    tags_list = [(x['name'], x['name']) for x in client.list_tags().json()]
    domains_list = []
    for d in doms:
        form = DomainForm(initial={'did': d['id']}, prefix=d['id'])
        form.fields['tags'].widget.choices = tags_list
        form.fields['tags'].initial = d['tags']
        domains_list.append((d, form))

    res['domains'] = domains_list
    res['new_domain'] = new_domain

    return main_render(request, 'domains.html', res)


@login_required
def tags(request):
    res = {}
    tagform = TagForm()
    client = UwsgiItClient(request.session.get('username'), request.session.get('password'), settings.CONSOLE_API)
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
    return main_render(request, 'tags.html', res)
