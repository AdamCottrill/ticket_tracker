from django.forms import ModelForm, CharField, Textarea, BooleanField
from django.shortcuts import get_object_or_404
#from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import (Submit, Layout, ButtonHolder, Div,
                                 Fieldset, MultiField, Field)


from .models import Ticket, FollowUp

class TicketForm(ModelForm):

    description = CharField(
        widget=Textarea(
            attrs={'class': 'input-xxlarge',}),
    )

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)

        #import pdb; pdb.set_trace()
        
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
            self.fields['same_as_ticket'] = CharField(required=False, label="")
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
        '''

        if self.cleaned_data.get('duplicate'):
            original_pk = self.cleaned_data['same_as_ticket']
            original = get_object_or_404(Ticket, id=original_pk)
            if not original:
                 raise forms.ValidationError("Invalid ticket number.")
        
        return self.cleaned_data
            
            
    class Meta:
        model = FollowUp
        fields = ['comment']
