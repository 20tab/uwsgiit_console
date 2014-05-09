from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'console.views.home', name='home'),
    url(r'^me/$', 'console.views.me_page', name='me'),
    url(r'^logout/$', 'console.views.logout', name='logout'),
    url(r'^containers/(?P<id>\d+)?$', 'console.views.containers', name='containers'),
    url(r'^domains/$', 'console.views.domains', name='domains'),
    url(r'^tags/$', 'console.views.tags', name='tags'),

)

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
    )