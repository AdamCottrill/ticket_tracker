from django.conf.urls import patterns, url

from .views import (TicketListView, TicketDetailView, manage_tickets,
                    TicketCreateView, TicketUpdateView)
# from .models import Ticket

#info = {
#    'queryset':Ticket.objects.all(),
#}

#urlpatterns = patterns('django.views.generic.list_detail',
#    url(r'^$', 'object_list', info, name = "ticket_list"),
#    url(r'^(?P<object_id>\d+)/$', 'object_detail',
#        info, name = "ticket_detail"),   
#)
#


urlpatterns = patterns('',
                url(regex = r"^$",
                    view = TicketListView.as_view(),
                    name="ticket_list"),
                       
                url(r'^(?P<pk>\d+)/$',
                    view = TicketDetailView.as_view(),
                    name = "ticket_detail"),
                       
                url(r"^all/$", manage_tickets),

                url(regex = r"^new/$",
                    view = TicketCreateView.as_view(),
                    name="new_ticket"),
                       
                url(r'^(?P<pk>\d+)/$',
                    view = TicketUpdateView.as_view(),
                    name = "update_ticket"),

                       
)
