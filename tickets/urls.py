from django.conf.urls import patterns, url

from .views import (TicketListView, TicketDetailView, manage_tickets,
                     TicketUpdateView, upvote_ticket, TicketFollowUpView,)
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
                    #view = TicketCreateView.as_view(),
                    #view = TicketCreateView,
                    view = TicketUpdateView,                    
                    name="new_ticket"),
                       
                url(r'^update/(?P<pk>\d+)/$',
                    #view = TicketUpdateView.as_view(),
                    view = TicketUpdateView,
                    name = "update_ticket"),

                url(r'^upvote/(?P<pk>\d+)/$',
                    view = upvote_ticket,
                    name = 'upvote_ticket'),

                url(r'^close/(?P<pk>\d+)/$',
                    view = TicketFollowUpView, kwargs={'close':True}, 
                    name = 'close_ticket'), 
                       
                url(r'^comment/(?P<pk>\d+)/$',
                    view = TicketFollowUpView, kwargs= {'close':False},
                    name = 'comment_ticket')
                       
                       
)
