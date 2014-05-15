from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic.list import ListView
from django.views.generic import DetailView


from .models import Ticket, UserVoteLog, FollowUp
from .forms import TicketForm, CloseTicketForm, SplitTicketForm, CommentForm
from .utils import is_admin


class TicketDetailView(DetailView):
    '''
    A view to render details of a single ticket.

    **Context:**

    ``object``
        a :model:`ticket.Ticket` object.

    ``comments``
        a list of :model:`tickets.FollowUp` objects associated with this
        ticket.

    **Template:**

    :template:`/tickets/ticket_detail.html`

    '''
    model = Ticket

    def get_context_data(self, **kwargs):
        '''Get the comments associated with this ticket.  Only include
        the public comments unless  request.user is an admin or
        created the ticket
        '''
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        pk = context['ticket'].id
        ticket = Ticket.objects.get(id=pk)
        if is_admin(user) or user == ticket.submitted_by:
            comments = FollowUp.all_comments.filter(
                ticket__pk=pk).order_by('-created_on')
        else:
            comments = FollowUp.objects.filter(
                ticket__pk=pk).order_by('created_on')
        context['comments'] = comments
        return context


class TicketListViewBase(ListView):
    '''A base class for all ticket listviews.'''
    model = Ticket


class TicketListView(TicketListViewBase):
    '''
    A view to render a list of tickets. If a query string and/or a
    user is provided, they will be used to filter the queryset,
    otherwise all tickets are returned in reverse chronological
    order.

    **Context:**

    ``object_list``
        a list of :model:`ticket.Ticket` objects.

    **Template:**

    :template:`/tickets/ticket_list.html`

    '''

    def get_queryset(self):
        q = self.request.GET.get("q")
        userid = self.kwargs.pop('userid', None)
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            user = None

        # Fetch the queryset from the parent's get_queryset
        # Get the q GET parameter
        if user and q:
            #NOTE - there is currenly no way to get here from our
            # existing templates.
            return Ticket.objects.filter(
                submitted_by=user,
                description__icontains=q).order_by("-created_on")
        elif q:
            # return a filtered queryset
            return Ticket.objects.filter(
                description__icontains=q).order_by("-created_on")
        elif user:
            return Ticket.objects.filter(
                submitted_by=user).order_by("-created_on")
        else:
            # No q or user is specified so we return the full queryset
            return Ticket.objects.all().order_by("-created_on")


class ClosedTicketListView(TicketListViewBase):
    '''A list of only closed tickets.

    **Context:**

    ``object_list``
        a list of :model:`ticket.Ticket` objects where
        status is either 'closed', 'duplicate' or 'split'.

    **Template:**

    :template:`/tickets/ticket_list.html`

    '''

    def get_queryset(self):
        inactive_codes = ['closed', 'split', 'duplicate']
        return Ticket.objects.filter(
            status__in=inactive_codes).order_by("-created_on")


class OpenTicketListView(TicketListViewBase):
    '''A list of only open tickets.

    **Context:**

    ``object_list``
        a list of :model:`ticket.Ticket` objects where
        status is either 'new','accepted', 'assigned' or 'reopened'

    **Template:**

    :template:`/tickets/ticket_list.html`

'''

    def get_queryset(self):
        open_codes = ['new', 'accepted', 'assigned', 'reopened']
        return Ticket.objects.filter(
            status__in=open_codes).order_by("-created_on")


class BugTicketListView(TicketListViewBase):
    '''A list of only bug reports tickets.

    **Context:**

    ``object_list``
        a list of :model:`ticket.Ticket` objects where
        ticket_type=='bug'

    **Template:**

    :template:`/tickets/ticket_list.html`

'''
    def get_queryset(self):
        return Ticket.objects.filter(
            ticket_type='bug').order_by("-created_on")


class FeatureTicketListView(TicketListViewBase):
    '''A list of only feature request tickets.

    **Context:**

    ``object_list``
        a list of :model:`ticket.Ticket` objects where
        ticket_type=='feature'

    **Template:**

    :template:`/tickets/ticket_list.html`

'''

    def get_queryset(self):
        return Ticket.objects.filter(
            ticket_type='feature').order_by("-created_on")


@login_required
def TicketUpdateView(request, pk=None,
                     template_name='tickets/ticket_form.html'):
    '''A view to allow users to update existing tickets or create new
    ones.

    New tickets can be created by any logged in user, but only
    administrators or the tags original submitter can make changes to
    an existing ticket.

    If a primary key is include in the request, an attempt will be
    made to retrieve the associated ticket. If no primary key is
    included, a new ticket will be created.

    **Context:**

    ``form``
        an instance of a TicketForm

    **Template:**

    :template:`/tickets/ticket_form.html`

    '''

    if pk:
        ticket = get_object_or_404(Ticket, pk=pk)
        if not (request.user == ticket.submitted_by or
                is_admin(request.user)):
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        ticket = Ticket(submitted_by=request.user, status='new')

    if request.POST:
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            new_ticket = form.save()
            return HttpResponseRedirect(new_ticket.get_absolute_url())
    else:
        form = TicketForm(instance=ticket)

    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))


@login_required
def SplitTicketView(request, pk=None,
                    template_name='tickets/split_ticket_form.html'):
    '''
    If a ticket is too complex to handle as a single issue, this
    view allows administrators to split the ticket into two child
    tickets.  The orginial ticket is closed, but is referenced by the
    children.  By default, all of the fields in the child ticket are
    set to the values for the same field in the parent.

    **Context:**

    ``form``
        an instance of a SplitTicketForm

    **Template:**

    :template:`/tickets/split_ticket_form.html`

    '''

    try:
        ticket = Ticket.objects.get(id=pk)
    except Ticket.DoesNotExist:
        url = reverse('ticket_list')
        return HttpResponseRedirect(url)

    if is_admin(request.user) is False:
        return HttpResponseRedirect(ticket.get_absolute_url())

    #start with the same data in both tickets as the original.
    initial = {
        'status1': 'new',
        'ticket_type1': ticket.ticket_type,
        'priority1': ticket.priority,
        'application1': ticket.application,        
        'assigned_to1': ticket.assigned_to,
        'description1': ticket.description,
        'status2': 'new',
        'ticket_type2': ticket.ticket_type,
        'priority2': ticket.priority,
        'application2': ticket.application,                
        'assigned_to2': ticket.assigned_to,
        'description2': ticket.description}

    if request.method == 'POST':
        form = SplitTicketForm(data=request.POST, user=request.user,
                               original_ticket=ticket)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        form = SplitTicketForm(initial=initial,
                               user=request.user, original_ticket=ticket)
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=RequestContext(request))


@login_required
def TicketFollowUpView(request, pk, action='close',
                       template_name='tickets/comment_form.html'):
    '''
    This view is used by administrators to close and re-open tickets.
    Tickets can be closed outright or as a duplicate.  In all cases a
    comment (explanation) is required.

   **Context:**

    ``ticket``
        a :model:`ticket.Ticket` object.

    ``form``
        an instance of a CloseTicketForm

    **Template:**

    :template:`/tickets/comment_form.html`

    '''

    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        url = reverse('ticket_list')
        return HttpResponseRedirect(url)

    if not is_admin(request.user):
        return redirect(ticket.get_absolute_url())
    if request.POST:
        form = CloseTicketForm(request.POST, ticket=ticket,
                               user=request.user, action=action)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
        else:
            render_to_response(template_name,
                               {'form': form, 'ticket': ticket},
                               context_instance=RequestContext(request))
    else:
        form = CloseTicketForm(ticket=ticket, user=request.user,
                               action=action)
    return render_to_response(template_name,
                              {'form': form, 'ticket': ticket},
                              context_instance=RequestContext(request))


#==============================
@login_required
def TicketCommentView(request, pk,
                      template_name='tickets/comment_form.html'):

    '''

    Add a comment to a ticket (i.e. create a new :model:FollowUp
    object).  No actions are associated with the new FollowUp object.

   **Context:**

    ``ticket``
        a :model:`ticket.Ticket` object.

    ``form``
        an instance of a CommentForm

    **Template:**

    :template:`/tickets/comment_form.html`

    '''

    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        url = reverse('ticket_list')
        return HttpResponseRedirect(url)

    if request.POST:
        form = CommentForm(request.POST, ticket=ticket,
                           user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
        else:
            render_to_response(template_name,
                               {'form': form, 'ticket': ticket},
                               context_instance=RequestContext(request))
    else:
        form = CommentForm(ticket=ticket, user=request.user)
    return render_to_response(template_name,
                              {'form': form, 'ticket': ticket},
                              context_instance=RequestContext(request))


@login_required
def upvote_ticket(request, pk):
    '''A view to increment the vote count for a ticket.  Only allow
    votes if user has logged in and then only if they have not voted
    for this ticket yet.'

    No template is rendered in this view.  The user is immediately
    re-directed back to the detail view for the ticket in question.

    '''
    ticket = Ticket.objects.get(pk=pk)
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        user = None

    if user:
        p, created = UserVoteLog.objects.get_or_create(ticket=ticket,
                                                       user=user)
        if ticket and created:
            ticket.up_vote()
    return HttpResponseRedirect(ticket.get_absolute_url())
