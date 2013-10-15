from django.conf.urls import patterns, url

from .views import (TicketListView, TicketDetailView, manage_tickets,
                    TicketUpdateView, upvote_ticket, TicketFollowUpView,
                    SplitTicketView)


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
                    view = TicketFollowUpView, kwargs={'action':'closed'}, 
                    name = 'close_ticket'), 
                url(r'^reopen/(?P<pk>\d+)/$',
                    view = TicketFollowUpView, kwargs={'action':'reopened'}, 
                    name = 'reopen_ticket'), 
                       
                url(r'^comment/(?P<pk>\d+)/$',
                    view = TicketFollowUpView, kwargs= {'action':'no_action'},
                    name = 'comment_ticket'),

                url(r'^split/(?P<pk>\d+)/$',
                    view = SplitTicketView,
                    name = "split_ticket"),
                       
                       
)
