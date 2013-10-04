# Create your views here.
from django import forms
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.views.generic.list import ListView
from django.views.generic import CreateView, UpdateView, DetailView

from .models import Ticket

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

    
class TicketUpdateView(UpdateView):
    model = Ticket
    