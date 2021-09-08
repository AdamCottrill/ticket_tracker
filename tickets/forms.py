from django.contrib.auth import get_user_model
from django.forms import (
    BooleanField,
    CharField,
    Form,
    IntegerField,
    ModelChoiceField,
    ModelForm,
    Textarea,
    TextInput,
    ValidationError,
)
from django.forms.widgets import CheckboxInput, Select
from taggit.forms import TagWidget

from .models import Application, FollowUp, Ticket, TicketDuplicate
from .utils import is_admin

User = get_user_model()


class UserModelChoiceField(ModelChoiceField):
    """a custom model choice widget for user objects.  It will
    display user first and last name in list of available choices
    (rather than their official user name). modified from
    https://docs.djangoproject.com/en/dev/ref/forms/fields/#modelchoicefield.
    """

    def label_from_instance(self, obj):
        if obj.first_name:
            label = "{0} {1}".format(obj.first_name, obj.last_name)
        else:
            label = obj.__str__()
        return label


class TicketForm(ModelForm):
    """A model form associated with ticket objects.  Allows tickets to be
    created and updated

    The ticket form needs to dynamically reflect the status of the
    ticket and facilitate the progression from new to completed.

    #status will rarely be needed on the form but will be inferred
    #from the action of the user.

    - freshly created tickets will be 'New' by default.

    - tickets can then be accepted or accepted and assigned by an
      admin depending on whether or not the assigned to field is
      filled out by the admin
    """

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        fields = [
            "title",
            "ticket_type",
            "priority",
            "application",
            "description",
            "tags",
        ]

        widgets = {
            "title": TextInput(attrs={"class": "form-control"}),
            "ticket_type": Select(attrs={"class": "form-control"}),
            "priority": Select(attrs={"class": "form-control"}),
            "application": Select(attrs={"class": "form-control"}),
            "description": Textarea(attrs={"class": "form-control", "rows": 10}),
            "tags": TextInput(attrs={"class": "form-control"}),
            "tags": TagWidget(
                attrs={
                    "class": "form-control",
                    "help_text": "<em>A comma separated list of tags.</em>",
                }
            ),
        }


class SplitTicketForm(Form):
    """
    This form is used to split an existing ticket into two separate tickets.
    Values from the first ticket are autopopulated with the values from the
    original.  This form is only accessible to admin users.

    Args: Form (django.forms.Form): django form class
    """

    status1 = CharField(
        max_length=20,
        label="Ticket Status",
        widget=Select(choices=Ticket.TICKET_STATUS_CHOICES),
    )

    ticket_type1 = CharField(
        max_length=20,
        label="Ticket Type",
        widget=Select(choices=Ticket.TICKET_TYPE_CHOICES),
    )

    title1 = CharField(max_length=80, label="Title")

    priority1 = CharField(
        max_length=20,
        label="Priority",
        widget=Select(choices=Ticket.TICKET_PRIORITY_CHOICES),
    )

    assigned_to1 = UserModelChoiceField(
        # queryset=User.objects.filter(groups__name="admin"),
        queryset=User.objects.all(),
        label="Assigned To",
        required=False,
    )

    description1 = CharField(
        label="Description", widget=Textarea(attrs={"class": "input-xxlarge"})
    )

    application1 = ModelChoiceField(
        queryset=Application.objects.all(), label="Application"
    )

    status2 = CharField(
        max_length=20,
        label="Ticket Status",
        widget=Select(choices=Ticket.TICKET_STATUS_CHOICES),
    )

    ticket_type2 = CharField(
        max_length=20,
        label="Ticket Type",
        widget=Select(choices=Ticket.TICKET_TYPE_CHOICES),
    )
    title2 = CharField(max_length=80, label="Title")

    priority2 = CharField(
        max_length=20,
        label="Priority",
        widget=Select(choices=Ticket.TICKET_PRIORITY_CHOICES),
    )

    assigned_to2 = UserModelChoiceField(
        # queryset=User.objects.filter(groups__name="admin"),
        queryset=User.objects.all(),
        label="Assigned To",
        required=False,
    )

    application2 = ModelChoiceField(
        queryset=Application.objects.all(), label="Application"
    )

    description2 = CharField(
        label="Description", widget=Textarea(attrs={"class": "input-xxlarge"})
    )

    comment = CharField(widget=Textarea(attrs={"class": "input-xxlarge"}))

    def __init__(self, user, original_ticket, *args, **kwargs):
        self.original_ticket = original_ticket
        self.user = user
        super(SplitTicketForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

    def save(self):

        original = self.original_ticket

        ticket1 = Ticket(
            status=self.cleaned_data["status1"],
            title=self.cleaned_data["title1"],
            assigned_to=self.cleaned_data.get("assigned_to1"),
            priority=self.cleaned_data.get("priority1"),
            application=self.cleaned_data.get("application1"),
            ticket_type=self.cleaned_data.get("ticket_type1"),
            description=self.cleaned_data.get("description1"),
            submitted_by=original.submitted_by,
            parent=original,
        )
        ticket1.save()

        ticket2 = Ticket(
            status=self.cleaned_data.get("status2"),
            title=self.cleaned_data["title2"],
            assigned_to=self.cleaned_data.get("assigned_to2"),
            priority=self.cleaned_data.get("priority2"),
            application=self.cleaned_data.get("application2"),
            ticket_type=self.cleaned_data.get("ticket_type2"),
            description=self.cleaned_data.get("description2"),
            submitted_by=original.submitted_by,
            parent=original,
        )
        ticket2.save()

        followup = FollowUp(
            ticket=original,
            submitted_by=self.user,
            comment=self.cleaned_data.get("comment"),
            action="closed",
        )
        followup.save()

        original.status = "split"
        original.save()


class CloseTicketForm(ModelForm):
    """
    This form will be used to close tickets either outright or as a
    duplicate.  It is also used to re-open closed tickets.  In each
    case a comment is required.

    """

    comment = CharField(widget=Textarea(attrs={"class": "input-xxlarge"}))

    def __init__(self, *args, **kwargs):
        self.action = kwargs.pop("action", "no_action")
        self.ticket = kwargs.pop("ticket")
        self.user = kwargs.pop("user")

        super(CloseTicketForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"

        if self.action == "closed":
            self.fields["duplicate"] = BooleanField(required=False)
            self.fields["same_as_ticket"] = IntegerField(
                required=False, label="Same as Ticket"
            )

    def clean_same_as_ticket(self):
        """make sure that we're not duplicating ourselves"""

        same_as_ticket = self.cleaned_data.get("same_as_ticket")
        if same_as_ticket == self.ticket.id:
            errmsg = "Invalid ticket number. A ticket cannot duplicate itself."
            raise ValidationError(errmsg)
        else:
            return same_as_ticket

    def clean(self):
        """
        If duplicate is True, we need to make sure that
        "same_as_ticket" is populated with a legitimate ticket number.
        Return validation errors if duplicate is checked but ticket
        number is blank, a ticket is provided but duplicate is
        unchecked, or if a ticket is provided but does not appear to
        be associated with an existing ticket.
        """

        if self.cleaned_data.get("same_as_ticket") and not self.cleaned_data.get(
            "duplicate"
        ):
            msg = "Duplicate is false and a ticket number was provided."
            raise ValidationError(msg)

        elif self.cleaned_data.get("duplicate") and not self.cleaned_data.get(
            "same_as_ticket"
        ):
            msg = "Duplicate is true but no ticket number is provided."
            raise ValidationError(msg)
        else:
            original_pk = self.cleaned_data.get("same_as_ticket")

        if self.cleaned_data.get("duplicate") and original_pk:
            try:
                original = Ticket.objects.get(id=original_pk)
            except Ticket.DoesNotExist:
                original = None
            if not original:
                raise ValidationError("Invalid ticket number.")
        return self.cleaned_data

    def save(self, *args, **kwargs):
        followUp = FollowUp(
            ticket=self.ticket,
            submitted_by=self.user,
            private=self.cleaned_data.get("private", False),
            comment=self.cleaned_data["comment"],
        )

        ticket = Ticket.objects.get(id=self.ticket.id)

        if self.action == "closed" or self.action == "reopened":
            ticket.status = self.action
            followUp.action = self.action

        if self.cleaned_data.get("duplicate"):
            original_pk = self.cleaned_data["same_as_ticket"]
            original = Ticket.objects.get(pk=original_pk)
            dup_ticket = TicketDuplicate(ticket=ticket, original=original)
            dup_ticket.save()

            ticket.status = "duplicate"
            followUp.action = "closed"

        followUp.save()
        ticket.save()

    class Meta:
        model = FollowUp
        fields = ["comment"]


class CommentTicketForm(ModelForm):
    """
    Make comment on a ticket without changing its status or who it is
    assigned to.
    """

    comment = CharField(widget=Textarea(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):

        self.ticket = kwargs.pop("ticket")
        self.user = kwargs.pop("user")
        super(CommentTicketForm, self).__init__(*args, **kwargs)

        if is_admin(self.user) or self.user == self.ticket.submitted_by:
            self.fields["private"] = BooleanField(
                required=False,
                label="Private (only visible to logged in users).",
                widget=CheckboxInput(attrs={"class": "form-check-input"}),
            )

    def save(self, *args, **kwargs):
        followUp = FollowUp(
            ticket=self.ticket,
            submitted_by=self.user,
            private=self.cleaned_data.get("private", False),
            comment=self.cleaned_data["comment"],
        )

        followUp.save()

    class Meta:
        model = FollowUp
        fields = ["comment"]


class AcceptTicketForm(ModelForm):
    """Accept a ticket and provide a comment."""

    comment = CharField(widget=Textarea(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):

        self.ticket = kwargs.pop("ticket")
        self.user = kwargs.pop("user")
        super(AcceptTicketForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        followUp = FollowUp(
            ticket=self.ticket,
            submitted_by=self.user,
            comment=self.cleaned_data["comment"],
        )

        if not is_admin(self.user):
            self.ticket.assigned_to = self.user
        self.ticket.status = "accepted"
        self.ticket.save()
        followUp.save()

    class Meta:
        model = FollowUp
        fields = ["comment"]


class AssignTicketForm(ModelForm):
    """Accept and Assign or re-assign a ticket and provide a
    comment."""

    comment = CharField(widget=Textarea(attrs={"class": "form-control"}))

    assigned_to = UserModelChoiceField(
        # queryset=User.objects.filter(groups__name='admin'),
        queryset=User.objects.filter(is_staff=True),
        label="Assign To",
        required=True,
        widget=Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user")
        self.ticket = kwargs.pop("ticket")
        super(AssignTicketForm, self).__init__(*args, **kwargs)
        if self.ticket.assigned_to:
            self.initial["assigned_to"] = self.ticket.assigned_to

    def save(self, *args, **kwargs):
        followUp = FollowUp(
            ticket=self.ticket,
            submitted_by=self.user,
            comment=self.cleaned_data["comment"],
        )

        assigned_to = self.cleaned_data.get("assigned_to")
        self.ticket.assigned_to = assigned_to
        self.ticket.status = "assigned"
        self.ticket.save()
        followUp.save()

    class Meta:
        model = FollowUp
        fields = ["comment"]
