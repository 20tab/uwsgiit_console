from __future__ import unicode_literals, absolute_import
from datetime import datetime
import json

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse,\
    HttpResponseForbidden, Http404
from django.template.loader import render_to_string

from .utils import ConsoleClient as CC

from .decorators import login_required
from .forms import LoginForm, MeForm, SSHForm, ContainerForm, TagForm,\
    DomainForm, NewDomainForm, CalendarForm, LoopboxForm, NewLoopboxForm,\
    AlarmForm


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('/')


def main_render(request, template, v_dict={}):
    username = request.session.get('username', False)
    password = request.session.get('password', False)
    api_url = request.session.get('api_url', False)

    if username and password and api_url:
        client = CC(username, password, api_url)

        v_dict['containers'] = sorted(
            client.containers().json(), key=lambda k: k['name'])
        last_alarm = client.alarms({'range': 1}).json()
        if last_alarm:
            v_dict['last_alarm_id'] = last_alarm[0]['id']

    return render(request, template, context=v_dict)


def home(request):
    v_dict = {}
    if 'action_login' in request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            request.session['username'] = cd['username']
            request.session['password'] = cd['password']
            request.session['api_url'] = cd['api_url'].url
            return HttpResponseRedirect('/me/')
    else:
        login_form = LoginForm()

    username = request.session.get('username', None)
    password = request.session.get('password', None)
    api_url = request.session.get('api_url', settings.DEFAULT_API_URL)

    client = CC(username, password, api_url)

    news = client.news().json()
    for n in news:
        n['date'] = datetime.fromtimestamp(n['date'])

    v_dict['news'] = news

    if client.username is None:
        v_dict['login_form'] = login_form
    else:
        if 'del-alarm' in request.GET:
            client.delete_alarm(request.GET['del-alarm'])

        v_dict['alarms'] = client.alarms({'range': 10}).json()
        if 'error' in v_dict['alarms']:
            return logout(request)

        for a in v_dict['alarms']:
            a['unix'] = datetime.fromtimestamp(a['unix'])

    return main_render(request, 'console/index.html', v_dict)


@login_required
def me_page(request):
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    me = client.me().json()
    if 'error' in me:
        return logout(request)

    v_dict = {'me': me}
    me_form = MeForm(initial={
        'company': me['company'],
        'email': me['email'],
        'password': request.session.get('password'),
        're_password': request.session.get('password'),
        'vat': me['vat']
    })

    if request.POST:
        me_form = MeForm(request.POST)
        if me_form.is_valid():
            cd = me_form.cleaned_data
            client.update_me({
                'company': cd['company'],
                'email': cd['email'],
                'password': cd['password'],
                'vat': cd['vat']
            })
            request.session['password'] = cd['password']

    v_dict['me_form'] = me_form
    v_dict['distros'] = client.distros().json()

    return main_render(request, 'console/me.html', v_dict)


@login_required
def containers(request, id):
    res = {}
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))
    if id:
        container = client.container(id).json()
        if 'error' in container:
            return logout(request)

        # Get last quota metric
        quota_metrics = client.container_metric(id, 'quota', None).json()
        if len(quota_metrics) > 0:
            used_quota = quota_metrics[-1][1]
            used_quota /= 1024 * 1024
        # If there are no metrics (in case of new container)
        else:
            used_quota = 0

        res['container'] = container

        distros_list = sorted(client.distros().json(), key=lambda distro: distro['id'], reverse=True)
        distros_list = [(x['id'], x['name']) for x in distros_list]

        tag_list = client.get_tag_list()

        containers_actual_linked_to = [x for x in client.containers().json() if x['uid'] != int(id)]

        linked_to = [(x['uid'], '{} ({})'.format(
            x['name'], x['uid'])) for x in containers_actual_linked_to]

        containerform = ContainerForm(
            tag_choices=tag_list,
            linked_to_choices=linked_to,
            distro_choices=distros_list,
            initial=container
        )
        sshform = SSHForm()
        calendar = CalendarForm()
        newloopboxform = NewLoopboxForm()

        container_copy = {k: container[k] for k in container if k not in containerform.fields}
        del container_copy['ssh_keys']
        del container_copy['distro_name']

        container_copy['storage'] = str(used_quota) + ' / ' + str(container_copy['storage']) + ' MB'
        container_copy['memory'] = str(container_copy['memory']) + 'MB'

        res['container_copy'] = container_copy

        active_panel = None
        if request.POST:
            if 'distro' in request.POST:
                containerform = ContainerForm(
                    request.POST,
                    tag_choices=tag_list,
                    linked_to_choices=linked_to,
                    distro_choices=distros_list)

                if containerform.is_valid():
                    cd = containerform.cleaned_data
                    container_updates = {
                        'distro': cd['distro'],
                        'tags': cd['tags'],
                        'note': cd['note'],
                        'nofollow': cd['nofollow'],
                        'quota_threshold': cd['quota_threshold']
                    }

                    optional_values = (
                        'name', 'jid', 'jid_destinations', 'jid_secret',
                        'alarm_freq', 'pushover_user', 'pushover_token',
                        'pushover_sound', 'pushbullet_token', 'slack_webhook',
                    )
                    for ov in optional_values:
                        if ov in cd:
                            container_updates[ov] = cd[ov]
                    if 'reboot' in cd and cd['reboot']:
                        container_updates['reboot'] = True
                    client.update_container(id, container_updates)

                    list_linked_to = [x['uid'] for x in containers_actual_linked_to]

                    for link in cd['linked_to']:
                        if link not in list_linked_to:
                            client.update_container(id, {'link': link})
                    for link in list_linked_to:
                        if link not in cd['linked_to']:
                            client.update_container(id, {'unlink': link})

            elif 'action' in request.POST:
                action = request.POST.get('action')
                active_panel = 'ssh'
                sshform = SSHForm(request.POST)
                if sshform.is_valid():
                    cd = sshform.cleaned_data
                    if action == 'add-key':
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
                        cd['key'] = cd['key'].strip()
                        if cd['key'] in container['ssh_keys']:
                            container['ssh_keys'].remove(cd['key'])
                            response = client.container_set_keys(id, container['ssh_keys'])
                            if response.status_code == 200:
                                messages.success(request, 'Key successfully removed')
                            else:
                                messages.error(request, 'An error occurred, please try again')

            else:
                active_panel = 'loopboxes'
                if 'mountpoint' in request.POST:
                    newloopboxform = NewLoopboxForm(request.POST)
                    if newloopboxform.is_valid():
                        cd = newloopboxform.cleaned_data
                        r = client.create_loopbox(id, cd['filename'], cd['mountpoint'])
                        if r.uerror:
                            newloopboxform.add_error(None, 'An error occurred: {}'.format(r.json()['error']))
                elif 'lid' in request.POST:
                    loopbox_form = LoopboxForm(request.POST, tag_choices=tag_list)
                    if loopbox_form.is_valid():
                        cd = loopbox_form.cleaned_data
                        lid = cd['lid']
                        tags_post = request.POST.getlist('{}-tags'.format(lid))
                        client.update_loopbox(lid, {'tags': tags_post})

        elif request.GET:
            if 'del-loopbox' in request.GET:
                active_panel = 'loopboxes'
                client.delete_loopbox(request.GET['del-loopbox'])
            if 'del-alarm' in request.GET:
                active_panel = 'alarms'
                client.delete_alarm(request.GET['del-alarm'])

        res['alarms'] = client.alarms({'container': id}).json()

        alarms_used_keys = ('a_color', 'a_container', 'a_class', 'a_level', 'a_vassal', 'a_filename', 'a_func', 'a_line')
        for k in alarms_used_keys:
            res[k] = set()

        for a in res['alarms']:
            a['unix'] = datetime.fromtimestamp(a['unix'])
            for k in a:
                if k != 'unix' and k != 'id' and k != 'msg' and a[k]:
                    res['a_{}'.format(k)].add(a[k])

        for k in alarms_used_keys:
            if res[k]:
                if k == 'a_level':
                    levels = {0: 'System', 1: 'User', 2: 'Exception', 3: 'Traceback', 4: 'Log'}
                    res[k] = [{'id': x, 'text': levels[x]} for x in res[k] if res[k]]
                else:
                    res[k] = [{'id': x, 'text': str(x)} for x in res[k] if res[k]]
                res[k] = json.dumps([{'id': '', 'text': ''}] + res[k])
            else:
                del res[k]

        loopboxes = client.loopboxes(container=id).json()

        loopboxes_list = []
        used_tags = []

        for l in loopboxes:
            form = LoopboxForm(initial={'lid': l['id'], 'tags': l['tags']}, prefix=l['id'], tag_choices=tag_list)
            loopboxes_list.append((l, form))
            used_tags.extend([tag for tag in l['tags'] if tag not in used_tags])

        res['loopboxes'] = loopboxes_list
        res['tags'] = used_tags

        containerform.fields['tags'].initial = container['tags']
        containerform.fields['linked_to'].initial = container['linked_to']

        res['containerform'] = containerform
        res['sshform'] = sshform
        res['calendar'] = calendar
        res['newloopboxform'] = newloopboxform
        res['active_panel'] = active_panel
    return main_render(request, 'console/containers.html', res)


@login_required
def domains_in_container(request, id):
    if request.is_ajax():

        client = CC(
            request.session.get('username'),
            request.session.get('password'),
            request.session.get('api_url')
        )

        rendered = render_to_string('console/container/domains.html', {'domains': client.domains_in_container(id).json()})
        return HttpResponse(
            json.dumps({'rendered': rendered}),
            content_type="application/json"
        )
    raise Http404


@login_required
def domains(request):
    res = {}
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    new_domain = NewDomainForm()
    calendar = CalendarForm()

    all_tags = client.list_tags().json()
    if 'error' in all_tags:
        return logout(request)

    tags_list = client.get_tag_list()

    if request.POST:
        if 'name' in request.POST:
            new_domain = NewDomainForm(request.POST)
            if new_domain.is_valid():
                name = new_domain.cleaned_data['name']
                r = client.add_domain(name)
                if r.uerror:
                    new_domain.add_error(None, 'Error: {}'.format(r.json()['error']))
                else:
                    messages.success(
                        request, 'domain {} successfully added'.format(name))
                    new_domain = NewDomainForm()
    if 'del' in request.GET:
        name = request.GET['del']
        client.delete_domain(name)

    doms = []
    for d in client.domains().json():
        name = d['name']
        if len(name.split('.')) > 2:
            name = '{}.{}'.format(name.split('.')[-2], name.split('.')[-1])
        d['key_name'] = name
        doms.append(d)

    doms = sorted(doms, key=lambda k: k['name'])
    doms = sorted(doms, key=lambda k: k['key_name'])
    domains_list = []
    used_tags = []

    for d in doms:
        form = DomainForm(initial={'tags': d['tags']}, prefix=d['id'], tag_choices=tags_list)
        domains_list.append((d, form))
        used_tags.extend([tag for tag in d['tags'] if tag not in used_tags])

    res['uuid'] = client.me().json()['uuid']
    res['domains'] = domains_list
    res['new_domain'] = new_domain
    res['calendar'] = calendar
    res['tags'] = used_tags

    return main_render(request, 'console/domains.html', res)


@login_required
def domain(request, id):
    calendar = CalendarForm()
    res = {}
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    all_tags = client.list_tags().json()
    if 'error' in all_tags:
        return logout(request)

    tags_list = client.get_tag_list()

    if request.POST:
        if 'tags' in request.POST or\
            'note' in request.POST:
            domain_form = DomainForm(data=request.POST, tag_choices=tags_list)
            if domain_form.is_valid():
                cd = domain_form.cleaned_data
                params = {}
                if 'tags' in cd:
                    params['tags'] = cd['tags']
                if 'note' in cd:
                    params['note'] = cd['note']
                client.update_domain(id, params)
    elif 'del' in request.GET:
        name = request.GET['del']
        client.delete_domain(name)

    domain = client.domain(id).json()
    form = DomainForm(tag_choices=tags_list, initial={
        'tags': domain['tags'], 'note': domain['note']})

    del domain['tags']
    del domain['note']

    res['calendar'] = calendar
    res['domain'] = domain
    res['domainform'] = form
    return main_render(request, 'console/domain.html', res)


@login_required
def containers_per_domain(request, id):
    if request.is_ajax():

        client = CC(
            request.session.get('username'),
            request.session.get('password'),
            request.session.get('api_url')
        )

        rendered = render_to_string('console/domain/containers.html', {'containers_per_domain': client.containers_per_domain(id).json()})
        return HttpResponse(
            json.dumps({'rendered': rendered}),
            content_type="application/json"
        )
    raise Http404


@login_required
def tags(request):
    res = {}
    tagform = TagForm()
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

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

    if 'error' in res['tags']:
        return logout(request)

    res['tagform'] = tagform
    return main_render(request, 'console/tags.html', res)


@login_required
def tag(request, tag):
    res = {}
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    res['tagged_domains'] = client.domains(tags=[tag]).json()
    if 'error' in res['tagged_domains']:
        return logout(request)
    res['tag'] = tag
    res['calendar_domains'] = CalendarForm(auto_id='calendar-domains-%s')
    res['calendar_containers'] = CalendarForm(auto_id='calendar-containers-%s')
    res['tagged_containers'] = client.containers(tags=[tag]).json()
    return main_render(request, 'console/tag.html', res)


@login_required
def alarms(request):
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))
    res = {}
    alarm_form = AlarmForm()
    alarms = client.alarms({'range': 100}).json()

    if 'error' in alarms:
        return logout(request)

    if request.POST:
        if 'action_filter' in request.POST:
            alarm_form = AlarmForm(request.POST)
            if alarm_form.is_valid():
                cd = alarm_form.cleaned_data
                cd['class'] = cd['class_']
                del cd['class_']
                r = client.alarms(cd)
                if r.uerror:
                    alarm_form.add_error(None, r.json()['error'])
                    alarms = ()
                else:
                    alarms = r.json()

    elif 'del-alarm' in request.GET:
            client.delete_alarm(request.GET['del-alarm'])

    for a in alarms:
        a['unix'] = datetime.fromtimestamp(a['unix'])
    res['alarm_form'] = alarm_form
    res['alarms'] = alarms
    return main_render(request, 'console/alarms.html', res)


@login_required
def latest_alarms(request):
    client = CC(request.session.get('username'),
                request.session.get('password'),
                request.session.get('api_url'))

    alarms = client.alarms({'range': 5})
    if 'error' in alarms:
        return logout(request)

    return HttpResponse(alarms.content)


@login_required
def alarm_key(request, id):
    if request.method == 'POST':
        client = CC(request.session.get('username'),
                    request.session.get('password'),
                    request.session.get('api_url'))
        r = client.create_alarm_key(id)
        return HttpResponse(r.content)
    return HttpResponseForbidden()


@login_required
def add_domain_tag(request, id):
    if request.method == 'POST' and '{}-tags'.format(id) in request.POST:
        client = CC(request.session.get('username'),
                    request.session.get('password'),
                    request.session.get('api_url'))
        tags_post = request.POST.getlist('{}-tags'.format(id))
        r = client.update_domain(id, {'tags': tags_post})
        return HttpResponse(r.content)
    return HttpResponseForbidden()


@login_required
def reboot_container(request, id):
    if request.method == 'POST':
        client = CC(request.session.get('username'),
                    request.session.get('password'),
                    request.session.get('api_url'))
        r = client.reboot_container(id)
        return HttpResponse(r.content)
    return HttpResponseForbidden()
