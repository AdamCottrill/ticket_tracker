# from django import template
from django import template
from django.template.defaultfilters import stringfilter
#from django.contrib.auth import user
from django.utils.safestring import mark_safe


register = template.Library()



@register.filter
@stringfilter
def priority_btn(priority, btn_size="xs"):
    '''given a ticket priority and button size, return a colour-coded
    bootstrap button with an appropriate label.
    '''

    btn_map = {
        '1': ['danger', 'Critical'],
        '2': ['warning', 'High'],
        '3': ['success', 'Normal'],
        '4': ['info', 'Low'],
        '5': ['default', 'Very Low'],        
    }

    #import pdb; pdb.set_trace()
    
    btn_attr = btn_map.get(priority)        
    btn = '<button type="button" class="btn btn-{0} btn-{1}">{2}</button>'
    btn = btn.format(btn_attr[0], btn_size, btn_attr[1])

    return mark_safe(btn)    

@register.filter
@stringfilter
def status_btn(status, btn_size='xs'):
    '''given a ticket status and button size, return a colour-coded
    bootstrap button with an appropriate label.
    '''

    btn_map = {
        'new':['success', 'New'],
        'accepted':['info', 'Accepted'],
        'assigned':['primary', 'Assigned'],
        'reopened':['warning', 'Reopened'],
        'closed':['default', 'Closed'],
        'duplicate':['default', 'Closed - Duplicate'],
        'split':['default', 'Closed - Split'],                   
    }

    btn_attr = btn_map.get(status.lower(), ['default', status])
    
    if btn_size == 'lg' and status in ('closed', 'duplicate', 'split'):
        btn_attr[0]='danger'

    btn = '<button type="button" class="btn btn-{0} btn-{1}">{2}</button>'
    btn = btn.format(btn_attr[0],  btn_size, btn_attr[1])

    return mark_safe(btn)
    
@register.filter
@stringfilter
def ticket_type_btn(ticket_type, btn_size="xs"):
    '''given a ticket type and button size, return a colour-coded
    bootstrap button with an appropriate label.
    '''
    
    btn_map = {
        'bug': ['danger', 'Bug Report'],
        'feature': ['default', 'Feature Request'],
    }
    
    btn_attr = btn_map.get(ticket_type.lower())        
    btn = '<button type="button" class="btn btn-{0} btn-{1}">{2}</button>'
    btn = btn.format(btn_attr[0],  btn_size, btn_attr[1])

    return mark_safe(btn)    


        
