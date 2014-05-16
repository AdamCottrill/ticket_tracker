from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

from tickets.views import TicketListView
                   

urlpatterns = patterns('',

                       #homepages
                       url(r'^$', TicketListView.as_view(), name='home'),
                       url(r'^$', TicketListView.as_view(), name='index'),
                       
                       url(r'^admin/doc/', 
                           include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^ticket/', include('tickets.urls')),
                       
                       url(r'^accounts/', include('simple_auth.urls')),
)

#note - this doesn't work as it should, but we're moving on for now.
if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^static/(?P<path>.*)$',
                                'django.views.static.serve',
                                {'document_root': settings.STATIC_ROOT}),
    )









