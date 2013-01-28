from django.conf.urls import patterns, include, url

from models import Ticket

info = {
    'queryset':Ticket.objects.all(),
}

urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^$', 'object_list', info, name = "ticket_list"),
    url(r'^(?P<object_id>\d+)/$', 'object_detail', info, name = "ticket_detail"),   
)
