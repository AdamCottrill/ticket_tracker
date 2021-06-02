"""
=============================================================
/home/adam/Documents/djcode/tickettracker/tickets/models.py
Created: 04 May 2014 21:26:46

DESCRIPTION:



A. Cottrill
=============================================================
"""


from django.db import models
from django.conf import settings
from django.contrib import admin

# from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify

from markdown2 import markdown

from taggit.managers import TaggableManager

from .utils import replace_links

LINK_PATTERNS = getattr(settings, "LINK_PATTERNS", None)

# for markdown2 (<h1> becomes <h3>)
DEMOTE_HEADERS = 2


class TicketManager(models.Manager):
    """A custom model manager for tickets.

    By default, only active tickets will be returned in any queryset.
    """

    def get_queryset(self):
        """only those tickets that are active"""
        # return self.filter(active=True)
        return super(TicketManager, self).get_queryset().filter(active=True)


class CommentManager(models.Manager):
    """A custom model manager for comments"""

    def get_queryset(self):
        """only those comments that are not private"""
        # return self.filter(private=False)
        return super(CommentManager, self).get_queryset().filter(private=False)


class Application(models.Model):
    """A model to keep track of which application a ticket is
    associated with.  The ticketTracker applicaton is likely to be
    used to support several differnt application.  This table will
    help us keep track of tickets are associated with which app.

    Use the admin to add, update or remove applications.

    """

    application = models.CharField(max_length=20)
    slug = models.SlugField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        """
        A customized save method foe each application so that a unique
        slug can be created. Used for url filtering.

        from:http://stackoverflow.com/questions/7971689/
             generate-slug-field-in-existing-table

        Slugify name if a slug  doesn't already exist.

        """

        self.slug = slugify(self.application)
        super(Application, self).save(*args, **kwargs)

    def __str__(self):
        return self.application


class Ticket(models.Model):
    """A model for ticket objects.

    This model used a custom model manager (TicketManager) to return
    only active tickets by default.  To return all tickets use
    all_tickets.all()

    """

    TICKET_STATUS_CHOICES = [
        ("new", "New"),
        ("accepted", "Accepted"),
        ("assigned", "Assigned"),
        ("re-opened", "Re-Opened"),
        ("closed", "Closed"),
        ("duplicate", "Closed - Duplicate"),
        ("split", "Closed - Split"),
    ]

    TICKET_TYPE_CHOICES = [
        ("feature", "Feature Request"),
        ("bug", "Bug Report"),
        ("task", "Task"),
    ]

    TICKET_PRIORITY_CHOICES = [
        (1, "Critical"),
        (2, "High"),
        (3, "Normal"),
        (4, "Low"),
        (5, "Very Low"),
    ]

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        on_delete=models.CASCADE,
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="submitted_tickets",
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20, choices=TICKET_STATUS_CHOICES, default=True, db_index=True
    )
    ticket_type = models.CharField(
        max_length=10, choices=TICKET_TYPE_CHOICES, default=True, db_index=True
    )
    title = models.CharField(max_length=80)
    description = models.TextField()
    description_html = models.TextField(editable=False, blank=True)
    priority = models.IntegerField(choices=TICKET_PRIORITY_CHOICES, db_index=True)
    created_on = models.DateTimeField("date created", auto_now_add=True)
    updated_on = models.DateTimeField("date updated", auto_now=True)
    votes = models.IntegerField(default=0)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)

    tags = TaggableManager(blank=True)

    all_tickets = models.Manager()
    objects = TicketManager()

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        name = self.description.split("\n", 1)[0]
        name = name[:30]
        return name

    def name(self):
        name = self.description.split("\n", 1)[0]
        name = name[:60]
        return name

    def get_absolute_url(self):
        url = reverse("tickets:ticket_detail", kwargs={"pk": self.id})
        return url

    def save(self, *args, **kwargs):
        self.description_html = markdown(
            self.description, extras={"demote-headers": DEMOTE_HEADERS}
        )
        self.description_html = replace_links(
            self.description_html, link_patterns=LINK_PATTERNS
        )

        super(Ticket, self).save(*args, **kwargs)

    def up_vote(self):
        """A method to increment the number of votes associated with a
        ticket."""
        self.votes += 1
        self.save()

    def down_vote(self):
        """A method to decrement the number of votes associated with a
        ticket."""
        if self.votes > 0:
            self.votes -= 1
            self.save()

    def duplicate_of(self, original_pk):
        """a method to flag this ticket as a duplicate of another.
        Automatically created an appropriate record in TicketDuplicate
        table.
        """
        original = Ticket.objects.get(pk=original_pk)
        duplicate = TicketDuplicate(ticket=self, original=original)
        duplicate.save()

    def get_duplicates(self):
        """a method to retreive all of the ticket objects that have
        been flagged as duplicates of this ticket.
        """
        duplicates = TicketDuplicate.objects.filter(original=self)
        if not duplicates:
            duplicates = None
        return duplicates

    def get_originals(self):
        """a method to retreive the ticket object that this ticket
        duplicates.
        """
        originals = TicketDuplicate.objects.filter(ticket=self)
        if not originals:
            originals = None
        return originals

    def get_parent(self):
        """a method to return the ticket that this ticket was split
        out of
        """
        if self.parent:
            try:
                parent = Ticket.objects.get(id=self.parent.id)
            except Ticket.DoesNotExist:
                parent = None
        else:
            parent = None
        return parent

    def get_children(self):
        """return any tickets that were create by splitting this
        ticket
        """
        children = Ticket.objects.filter(parent=self.id)
        if not children:
            children = None
        return children

    def is_closed(self):
        """a boolean method to indicate if this ticket is open or
        closed.  Makes templating much simpler.
        """
        if self.status in ("closed", "duplicate", "split"):
            return True
        else:
            return False


class TicketDuplicate(models.Model):
    """A simple table to keep track of which tickets are duplicates of
    which ticket.

    """

    ticket = models.ForeignKey(
        Ticket, related_name="duplicate", on_delete=models.CASCADE
    )
    original = models.ForeignKey(
        Ticket, related_name="original", on_delete=models.CASCADE
    )

    def __str__(self):
        string = "Ticket {0} is a duplicate of ticket {1}"
        string = string.format(self.ticket.id, self.original.id)
        return string


class UserVoteLog(models.Model):
    """A table to keep track of which tickets a user has voted for.
    Each user can only upvote a ticket once.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)


class FollowUp(models.Model):
    """A model to hold comments and follow-up actions associated with a
    ticket.

    A FollowUp without any action is just a comment.  Valid actions
    for a followup include closed, reopened and split.

    """

    ACTION_CHOICES = [
        ("no_action", "No Action"),
        ("closed", "Closed"),
        ("re-opened", "Re-Opened"),
        ("split", "Split"),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_on = models.DateTimeField("date created", auto_now_add=True)
    comment = models.TextField()

    comment_html = models.TextField(editable=False, blank=True)
    # closed = models.BooleanField(default=False)

    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, default="no_action", db_index=True
    )
    private = models.BooleanField(default=False)

    objects = CommentManager()
    all_comments = models.Manager()

    def save(self, *args, **kwargs):
        self.comment_html = markdown(
            self.comment, extras={"demote-headers": DEMOTE_HEADERS}
        )
        self.comment_html = replace_links(
            self.comment_html, link_patterns=LINK_PATTERNS
        )

        super(FollowUp, self).save(*args, **kwargs)


class TicketAdmin(admin.ModelAdmin):
    date_heirarchy = "created_on"
    list_filter = ("status",)
    list_display = ("id", "name", "status", "assigned_to")
    search_field = ["description"]
