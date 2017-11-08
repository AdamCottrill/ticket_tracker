from django.conf.urls import patterns, url

#from .views import (TicketListView, TicketDetailView,
#                    TicketUpdateView, upvote_ticket, TicketFollowUpView,
#                    SplitTicketView)

from .views import *

urlpatterns = [

                url(r'^(?P<pk>\d+)/$',
                    view = TicketDetailView.as_view(),
                    name = "ticket_detail"),

                url(regex = r"^new/$",
                    view = TicketUpdateView,
                    name="new_ticket"),

                url(r'^update/(?P<pk>\d+)/$',
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
                    #view = TicketFollowUpView, kwargs= {'action':'no_action'},
                    view = TicketCommentView,
                    name = 'comment_ticket'),

                url(r'^split/(?P<pk>\d+)/$',
                    view = SplitTicketView,
                    name = "split_ticket"),

                #===========
                #Ticket Lists
                url(regex = r"^$",
                    view = TicketListView.as_view(),
                    name="ticket_list"),

                url(regex = r"^mytickets/(?P<userid>\d+|\-99)/$",
                    view = TicketListView.as_view(),
                    name="my_ticket_list"),

                url(regex = r"^open/$",
                    view = OpenTicketListView.as_view(),
                    name="open_tickets"),

                url(regex = r"^closed/$",
                    view = ClosedTicketListView.as_view(),
                    name="closed_tickets"),

                url(regex = r"^bugreports/$",
                    view = BugTicketListView.as_view(),
                    name="bug_reports"),

                url(regex = r"^featurerequests/$",
                    view = FeatureTicketListView.as_view(),
                    name="feature_requests"),
]
