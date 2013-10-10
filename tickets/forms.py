from django.forms import ModelForm, CharField, Textarea
#from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


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
        self.close = kwargs.pop('close', False)
        super(CommentForm, self).__init__(*args, **kwargs)

        #import pdb; pdb.set_trace()
        
        self.helper = FormHelper()
        self.helper.form_id = 'comment'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        if self.close:
            self.helper.add_input(Submit('submit', 'Close Ticket',
                                 css_class = 'btn btn-danger pull-right'))
        else:
            self.helper.add_input(Submit('submit', 'Post Comment',
                                 css_class = 'btn btn-default pull-right'))            
        
    class Meta:
        model = FollowUp
        fields = ['comment']
