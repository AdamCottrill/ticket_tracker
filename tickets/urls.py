from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    path("<int:pk>/", view=TicketDetailView.as_view(), name="ticket_detail"),
    path("new/", view=TicketUpdateView, name="new_ticket"),
    path("update/<int:pk>/", view=TicketUpdateView, name="update_ticket"),
    path("upvote/<int:pk>/", view=upvote_ticket, name="upvote_ticket"),
    path(
        "close/<int:pk>/",
        view=TicketCommentView,
        kwargs={"action": "closed"},
        name="close_ticket",
    ),
    path(
        "reopen/<int:pk>/",
        view=TicketCommentView,
        kwargs={"action": "reopened"},
        name="reopen_ticket",
    ),
    path(
        "accept/<int:pk>/",
        view=TicketCommentView,
        kwargs={"action": "accept"},
        name="accept_ticket",
    ),
    path(
        "assign/<int:pk>/",
        view=TicketCommentView,
        kwargs={"action": "assign"},
        name="assign_ticket",
    ),
    path(
        "comment/<int:pk>/",
        view=TicketCommentView,
        kwargs={"action": "comment"},
        name="comment_ticket",
    ),
    path("split/<int:pk>/", view=SplitTicketView, name="split_ticket"),
    # ===========
    # Ticket Lists
    path("", view=TicketListView.as_view(), name="ticket_list"),
    path(
        "mytickets/<str:username>/",
        view=TicketListView.as_view(),
        name="my_ticket_list",
    ),
    path(
        "assinged_to/<str:username>/",
        view=TicketListView.as_view(),
        name="assigned_to",
        kwargs={"what": "assigned_to"},
    ),
    path(
        "submitted_by/<str:username>/",
        view=TicketListView.as_view(),
        name="submitted_by",
        kwargs={"what": "submitted_by"},
    ),
    path(
        "open/",
        view=TicketListView.as_view(),
        name="open_tickets",
        kwargs={"status": "open"},
    ),
    path(
        "closed/",
        view=TicketListView.as_view(),
        name="closed_tickets",
        kwargs={"status": "closed"},
    ),
    path(
        "bugreports/",
        view=TicketListView.as_view(),
        name="bug_reports",
        kwargs={"type": "bug"},
    ),
    path(
        "featurerequests/",
        view=TicketListView.as_view(),
        name="feature_requests",
        kwargs={"type": "feature"},
    ),
    path(
        "tasks/", view=TicketListView.as_view(), name="tasks", kwargs={"type": "task"}
    ),
    # project tags
    # path('tag/<slug:slug>', TagIndexView.as_view(),
    #     name='tagged'),
    path(
        "tagged/<slug:slug>/", view=TagIndexView.as_view(), name="tickets_tagged_with"
    ),
]
