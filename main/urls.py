from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

from django.conf import settings
from django.conf.urls import include, url

from django.views.static import serve as serve_static

admin.autodiscover()

from tickets.views import TicketListView


urlpatterns = [
    #homepages
    url(r'^$', TicketListView.as_view(), name='home'),
    url(r'^$', TicketListView.as_view(), name='index'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),

    url(r'^ticket/', include('tickets.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),

#    url(r'^accounts/', include('simple_auth.urls')),
]

#note - this doesn't work as it should, but we're moving on for now.
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        url(r'^static/(?P<path>.*)$',
            serve_static,
            {'document_root': settings.STATIC_ROOT}),

        url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
