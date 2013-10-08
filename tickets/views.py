# Create your views here.
from django import forms
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
#from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView, DetailView


from .models import Ticket, UserVoteLog

TICKET_STATUS_CHOICES = {
    ('new', 'New'),
    ('accepted', 'Accepted'),
    ('assigned', 'Assigned'),
    ('reopened', 'Reopened'),
    ('closed', 'Closed'),    
}




class TicketDetailView(DetailView):
    model = Ticket

class TicketListView(ListView):
    model = Ticket

    
class TicketForm(forms.Form):
    #    status = forms.CharField()
    active = forms.BooleanField()
    status = forms.ChoiceField(choices = TICKET_STATUS_CHOICES)    
    description = forms.CharField()    

    #TicketFormSet = formset_factory(TicketForm)

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


class TicketCreateView(CreateView):
    model = Ticket

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TicketCreateView, self).dispatch(*args, **kwargs)
    

class TicketUpdateView(UpdateView):
    model = Ticket

    
@login_required
def upvote_ticket(request,pk):
    #ticket = Ticket.object.get(pk=pk)
    user = request.user
    ticket = get_object_or_404(Ticket, pk=pk)                    

    has_voted = UserVoteLog.objects.get_or_create(ticket=ticket,
                                                  user=user)
    if ticket and not has_voted:        
        ticket.up_vote()
    return HttpResponseRedirect(ticket.get_absolute_url())    
    #return render_to_response('tickets/ticket_detail.html',
    #                          {'object':ticket},
    #                          context_instance = RequestContext(request))
    
    
    
    