from django.contrib.auth.models import User
from django.forms import (Form, ModelForm, CharField, Textarea, BooleanField,
                          ValidationError, ModelChoiceField, IntegerField)
from django.forms.widgets import Select
from django.shortcuts import get_object_or_404

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Submit, Layout, ButtonHolder, Div, Fieldset,
                                 Field)


from .models import Ticket, FollowUp

class TicketForm(ModelForm):

    description = CharField(
        widget=Textarea(
            attrs={'class': 'input-xxlarge',}),
    )

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = 'ticket'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

        priorities = sorted(self.base_fields['priority'].choices,
                            key=lambda x:x[0], reverse=True)
        self.fields['priority'].choices = priorities
        
    class Meta:
        model = Ticket
        fields = ['status', 'ticket_type', 'priority', 'description',
                  'assigned_to']

        
class SplitTicketForm(Form):

    status1 = CharField(max_length=20,label="Ticket Status",
                              widget=Select(choices=
                                Ticket.TICKET_STATUS_CHOICES))
    
    ticket_type1 = CharField(max_length=20,label="Ticket Type",
                              widget=Select(choices=
                                Ticket.TICKET_TYPE_CHOICES))
    
    priority1 = CharField(max_length=20, label="Priority",
                              widget=Select(choices=
                                Ticket.TICKET_PRIORITY_CHOICES))

    assigned_to1 = ModelChoiceField(queryset=User.objects.all(),
                                    label="Assigned To", required=False)
    
    description1 = CharField( label="Description",
                              widget=Textarea(attrs={
                                  'class': 'input-xxlarge',}))
        
    status2 = CharField(max_length=20,label="Ticket Status",
                              widget=Select(choices=
                                Ticket.TICKET_STATUS_CHOICES))
    
    ticket_type2 = CharField(max_length=20, label="Ticket Type",
                              widget=Select(choices=
                                Ticket.TICKET_TYPE_CHOICES))
        
    priority2 = CharField(max_length=20, label="Priority",
                              widget=Select(choices=
                                Ticket.TICKET_PRIORITY_CHOICES))
    
    assigned_to2 = ModelChoiceField(queryset=User.objects.all(),
                                    label="Assigned To", required=False)
 
    description2 = CharField(label="Description", widget=Textarea(
            attrs={'class': 'input-xxlarge',}))
    
    comment = CharField(widget=Textarea(
            attrs={'class': 'input-xxlarge',}))

    
    def __init__(self, user, original_ticket, *args, **kwargs):
        self.original_ticket = original_ticket        
        self.user = user
        super(SplitTicketForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = 'splitticket'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset("Ticket 1",
                             'status1',
                             'ticket_type1',
                             'priority1',
                             'assigned_to1',
                             'description1'),
                    css_class='col-md-6 well'),
            Div(    
                Fieldset("Ticket 2",
                     'status2',
                     'ticket_type2',
                     'priority2',
                     'assigned_to2',
                     'description2'),
                css_class='col-md-6 well'),
            css_class='row'),
            'comment',
            ButtonHolder(Submit('submit', 'Split Ticket',
                                 css_class = 'btn btn-danger pull-right'))
        )

    def save(self):

        original = self.original_ticket 
        
        ticket1 = Ticket(status = self.cleaned_data['status1'],
                         assigned_to = self.cleaned_data.get('assigned_to1'),
                         priority = self.cleaned_data.get('priority1'),
                         ticket_type = self.cleaned_data.get('ticket_type1'),
                         description = self.cleaned_data.get('description1'),
                         submitted_by=original.submitted_by,
                         parent = original)
        ticket1.save()

        ticket2 = Ticket(status = self.cleaned_data.get('status2'),
                         assigned_to = self.cleaned_data.get('assigned_to2'),
                         priority = self.cleaned_data.get('priority2'),
                         ticket_type = self.cleaned_data.get('ticket_type2'),
                         description = self.cleaned_data.get('description2'),
                         submitted_by=original.submitted_by,
                         parent = original)
        ticket2.save()

        followup = FollowUp(ticket = original,
                            submitted_by=self.user,
                            comment = self.cleaned_data.get('comment'),
                            action = 'closed')
        followup.save()

        original.status = 'split'
        original.save()
        
                
class CommentForm(ModelForm):

    comment = CharField(
        widget=Textarea(
            attrs={'class': 'input-xxlarge',}),
    )

    def __init__(self, *args, **kwargs):
        self.action = kwargs.pop('action', 'no_action')
        super(CommentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'comment'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'

        #TODO - refactor this layout - all three options have comment
        # and button (with different labels)        
        if self.action == 'closed':
            self.fields['duplicate'] = BooleanField(required=False)
            self.fields['same_as_ticket'] = IntegerField(required=False,
                                                         label="")
            self.helper.layout = Layout(
                Div(
                    'comment',
                    Div(
                    Field('duplicate',css_class='col-md-3'),
                    Field('same_as_ticket',css_class='col-md-6',
                          placeholder='Same as ticket #'),
                        css_class='form-group form-inline'), 
                    css_class='row'),               
                ButtonHolder(Submit('submit', 'Close Ticket',
                                 css_class = 'btn btn-danger pull-right'))
                )
        elif self.action=='reopened':
            self.helper.layout = Layout(
                'comment',
                ButtonHolder(Submit('submit', 'Re-open Ticket',
                                 css_class = 'btn btn-default pull-right')))
        else:
            self.helper.layout = Layout(
                'comment',
                ButtonHolder(Submit('submit', 'Post Comment',
                                 css_class = 'btn btn-default pull-right')))
                            
    def clean(self):
        '''if duplicate is True, we need to make sure that
        "same_as_ticket" is populated with a legitimate ticket number.
        Return validation errors if duplicate is checke but ticket
        number is blank, a ticket is provided but duplicat is
        unchecked, or if a ticket is provided but does not appear to
        be associated with an existing ticket..
        '''

        if (self.cleaned_data.get('same_as_ticket') and not
            self.cleaned_data.get('duplicate')):
            
            raise ValidationError("Duplicate false, ticket number provided.")
            
        elif (self.cleaned_data.get('duplicate') and not
              self.cleaned_data.get('same_as_ticket')):
            raise ValidationError("Duplicate true, no ticket number provided.")
        else:        
            original_pk = self.cleaned_data.get('same_as_ticket')
            if original_pk:
                try:
                    original_pk = int(original_pk)
                except ValueError:
                    original_pk = None
        
        if self.cleaned_data.get('duplicate') and original_pk:
            try:
                original = Ticket.objects.get(id=original_pk)
            except Ticket.DoesNotExist:
                original = None
            if not original:
                 raise ValidationError("Invalid ticket number.")
            
        return self.cleaned_data            
            
    class Meta:
        model = FollowUp
        fields = ['comment']
