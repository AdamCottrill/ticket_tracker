from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list import ListView
from django.views.generic import DetailView


from .models import Ticket, UserVoteLog, FollowUp, TicketDuplicate
from .forms import TicketForm, CommentForm, SplitTicketForm 


class TicketDetailView(DetailView):
    '''A view to render details of a single ticket.'''
    model = Ticket

    def get_context_data(self, **kwargs):
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        
        pk = context['ticket'].id 
        comments = FollowUp.objects.filter(ticket__pk=pk
           ).order_by('-created_on')
        context['comments'] = comments
        return context


class TicketListViewBase(ListView):
    '''A base class for all ticket listviews.'''    
    model = Ticket


class TicketListView(TicketListViewBase):
    '''A view to render a list of tickets. if a query string and/or a
    user is provided, they will be used to filter the queryset,
    otherwise all tickets are returned in reverse chronological
    order.
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
    '''A list of only closed tickets.'''    
    
    def get_queryset(self):
        inactive_codes = ['closed', 'split','duplicate']
        return Ticket.objects.filter(
                status__in=inactive_codes).order_by("-created_on")

class OpenTicketListView(TicketListViewBase):
    '''A list of only open tickets.'''    
    
    def get_queryset(self):
        open_codes = ['new','accepted', 'assigned','reopened']
        return Ticket.objects.filter(
                status__in=open_codes).order_by("-created_on")


class BugTicketListView(TicketListViewBase):
    '''A list of only bug reports tickets.'''    
    
    def get_queryset(self):
        return Ticket.objects.filter(
                ticket_type='bug').order_by("-created_on")


class FeatureTicketListView(TicketListViewBase):
    '''A list of only feature request tickets.'''    
    
    def get_queryset(self):
        return Ticket.objects.filter(
                ticket_type='feature').order_by("-created_on")
        
    


            
    
@login_required
def TicketUpdateView(request, pk=None,
                     template_name='tickets/ticket_form.html'):
    '''A view to allow users to update existing tickets.  Only
    administrators or the tags original submitter can make changes to
    a ticket
    '''
    
    if pk:
        ticket = get_object_or_404(Ticket, pk=pk)
        if (request.user != ticket.submitted_by or
            request.user.is_staff() == False):
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
                              {'form': form,},
                              context_instance=RequestContext(request))

@login_required
def SplitTicketView(request, pk=None,
                     template_name='tickets/split_ticket_form.html'):
    '''If a ticket is too complex to handle in a single ticket, this
    view allows administrators to split the ticket into two child
    tickets.  The orginial ticket is closed, but is referenced by the
    children.  By default, all of the fields in the child ticket are
    set to the values for the same field in the parent.
    '''
        
    ticket = get_object_or_404(Ticket, pk=pk)

    try:
        ticket = Ticket.objects.get(id=pk)
    except User.DoesNotExist:
        url = reverse('ticket_list')
        return HttpResponseRedirect(url)
    
    #start with the same data in both tickets as the original.
    initial = {
            'status1':'new',
            'ticket_type1':ticket.ticket_type,
            'priority1':ticket.priority,
            'assigned_to1':ticket.assigned_to,
            'description1':ticket.description,
            'status2':'new',
            'ticket_type2':ticket.ticket_type,
            'priority2':ticket.priority,
            'assigned_to2':ticket.assigned_to,
            'description2':ticket.description}
    
    if request.method == 'POST':
        form = SplitTicketForm(data=request.POST, user = request.user,
                               original_ticket = ticket)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        form = SplitTicketForm(initial=initial,
                               user = request.user, original_ticket = ticket)
    return render_to_response(template_name,
                              {'form': form,},
                              context_instance=RequestContext(request))

    
@login_required
def TicketFollowUpView(request, pk, action='no_action',
                     template_name='tickets/comment_form.html'):
    
    '''Add a comment to a ticket.  If the user is an administrator,
    this view is also used to close and re-open tickets.
    '''
    
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        url = reverse('ticket_list')
        return HttpResponseRedirect(url)
    
    if request.POST:
        form = CommentForm(request.POST, action=action)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.submitted_by=request.user
            new_comment.ticket = ticket
            new_comment.action = action
            new_comment.save()

            if action == 'closed' or action == 'reopened':
                ticket.status=action
                ticket.save()
            if form.cleaned_data.get('duplicate'):
                original_pk=form.cleaned_data['same_as_ticket']
                original = Ticket.objects.get(pk=original_pk)
                dup_ticket = TicketDuplicate(ticket=ticket, original=original)
                dup_ticket.save()

                ticket.status= 'duplicate'
                ticket.save()
                
            return HttpResponseRedirect(ticket.get_absolute_url())
        else:
            render_to_response(template_name,
                              {'form': form, 'ticket':ticket},
                              context_instance=RequestContext(request))
    else:
        form = CommentForm(action=action)
            
    return render_to_response(template_name,
                              {'form': form, 'ticket':ticket},
                              context_instance=RequestContext(request))
    
@login_required
def upvote_ticket(request,pk):
    '''A view to increment the vote count for a ticket.  Only allow
    votes if user has logged in and then only if they have not voted
    for this ticket yet.'
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
    
    
    
    