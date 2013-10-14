# Create your views here.
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView, DetailView



from .models import Ticket, UserVoteLog, FollowUp, TicketDuplicate
from .forms import TicketForm, CommentForm 

TICKET_STATUS_CHOICES = {
    ('new', 'New'),
    ('accepted', 'Accepted'),
    ('assigned', 'Assigned'),
    ('reopened', 'Reopened'),
    ('closed', 'Closed'),    
}




class TicketDetailView(DetailView):
    model = Ticket


    def get_context_data(self, **kwargs):
        context = super(TicketDetailView, self).get_context_data(**kwargs)
        
        pk = context['ticket'].id 
        comments = FollowUp.objects.filter(ticket__pk=pk
           ).order_by('-created_on')
        context['comments'] = comments
        return context

    
class TicketListView(ListView):
    model = Ticket

    
#class TicketForm(forms.Form):
#    #    status = forms.CharField()
#    active = forms.BooleanField()
#    status = forms.ChoiceField(choices = TICKET_STATUS_CHOICES)    
#    description = forms.CharField()    
#
#    #TicketFormSet = formset_factory(TicketForm)

def manage_tickets(request):
    TicketFormSet = formset_factory(TicketForm)
    if request.method == 'POST':
        formset = TicketFormSet(request.POST, request.FILES)
        if formset.is_valid():
            # do something with the formset.cleaned_data
            pass
    else:
        tickets = Ticket.objects.all()
        initial_data =[]
        for ticket in tickets:
            ticket_dict ={'status':ticket.status,
                          'description':ticket.description}
            initial_data.append(ticket_dict)

        formset = TicketFormSet(initial = initial_data)
    return render_to_response('tickets/manage_tickets.html',
                              {'formset': formset})

@login_required
def TicketUpdateView(request, pk=None,
                     template_name='tickets/ticket_form.html'):
    if pk:
        ticket = get_object_or_404(Ticket, pk=pk)
        #if ticket.author != request.user:
        #    return HttpResponseForbidden()
    else:
        ticket = Ticket(submitted_by=request.user, status='new')

    if request.POST:
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            new_ticket = form.save()
            # If the save was successful, redirect to another page
            #redirect_url = reverse(ticket_save_success)
            #return HttpResponseRedirect(redirect_url)
            return HttpResponseRedirect(new_ticket.get_absolute_url())
            
    else:
        form = TicketForm(instance=ticket)

    return render_to_response(template_name,
                              {'form': form,},
                              context_instance=RequestContext(request))


@login_required
def TicketFollowUpView(request, pk, action='no_action',
                     template_name='tickets/comment_form.html'):

    ticket = Ticket.objects.get(pk=pk)
    #ticket = get_object_or_404(Ticket,pk)
    #form = CommentForm(ticket=ticket, submitted_by=request.user)    
    #import pdb; pdb.set_trace()
    
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
    ticket = Ticket.objects.get(pk=pk)
    user = request.user
    #ticket = get_object_or_404(Ticket, pk=pk)                    

    p, created = UserVoteLog.objects.get_or_create(ticket=ticket,
                                                  user=user)

    #import pdb; pdb.set_trace()
    if ticket and created:        
        ticket.up_vote()
    return HttpResponseRedirect(ticket.get_absolute_url())    
    #return render_to_response('tickets/ticket_detail.html',
    #                          {'object':ticket},
    #                          context_instance = RequestContext(request))
    
    
    
    