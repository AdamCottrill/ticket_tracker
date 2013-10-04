from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Ticket(models.Model):
    '''
    '''

    TICKET_STATUS_CHOICES = {
        ('new', 'New'),
        ('accepted', 'Accepted'),
        ('assigned', 'Assigned'),
        ('reopened', 'Reopened'),
        ('closed', 'Closed'),
        ('duplicate', 'Closed - Duplicate'),    
    }

    TICKET_TYPE_CHOICES = {
        ('feature', 'Feature Request'),
        ('but', 'Bug Report'),
        
    }

    TICKET_PRIORITY_CHOICES = {
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Normal'),
        (4, 'Low'),
        (5, 'Very Low'),        
    }
    
    
    assigned_to = models.ForeignKey(User, null=True, blank=True,
                                    related_name="assigned_tickets")
    submitted_by = models.ForeignKey(User, null=True, blank=True,
                                     related_name="submitted_tickets")
    status = models.CharField(max_length=20, 
                              choices=TICKET_STATUS_CHOICES, default=True)
    ticket_type = models.CharField(max_length=10, 
                              choices=TICKET_TYPE_CHOICES, default=True)
    description = models.TextField()
    #resolution = models.TextField()
    priority = models.IntegerField(choices=TICKET_PRIORITY_CHOICES)
    created_on = models.DateTimeField('date created', auto_now_add=True)
    updated_on = models.DateTimeField('date updated', auto_now=True)

    def name(self):
        return self.description.split("\n", 1)[0]

    def get_absolute_url(self):
        return str(self.id)

class FollowUp(models.Model):
    ''' '''
    ticket = models.ForeignKey(Ticket)
    submitted_by = models.ForeignKey(User, null=True, blank=True)    
    created_on = models.DateTimeField('date created', auto_now_add=True)
    comment = models.TextField()
    
class TicketAdmin(admin.ModelAdmin):
    date_heirarchy = "created_on"
    list_filter = ("status",)
    list_display = ("id", "name", "status", "assigned_to")
    search_field = ['description']

admin.site.register(Ticket, TicketAdmin)
