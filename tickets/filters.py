import django_filters

from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    """A filter class that will allow us to find tickets using url
    parameters.

    TODO - implement - recently opened and recently closed (in the
    last week and the last month)

    """

    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    priority = django_filters.CharFilter(field_name="priority", lookup_expr="exact")

    ticket_type = django_filters.CharFilter(
        field_name="ticket_type", lookup_expr="exact"
    )

    assigned_to = django_filters.CharFilter(
        field_name="assigned_to__username", lookup_expr="exact"
    )

    submitted_by = django_filters.CharFilter(
        field_name="submitted_by__username", lookup_expr="exact"
    )

    application = django_filters.CharFilter(
        field_name="application__slug", lookup_expr="exact"
    )

    tags = django_filters.CharFilter(field_name="tags__name", lookup_expr="exact")

    class Meta:
        model = Ticket
        fields = [
            "status",
            "ticket_type",
            "priority",
            "application__slug",
            "assigned_to__username",
            "submitted_by__username",
            "tags__name",
        ]
