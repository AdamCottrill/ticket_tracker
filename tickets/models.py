from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

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
        ('bug', 'Bug Report'),
        
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
    votes = models.IntegerField(default=0)
    parent = models.ForeignKey('self',
                                   blank=True,
                                   null=True)

    
    def name(self):
        name = self.description.split("\n", 1)[0]
        name = name[:60]
        return name

    def get_absolute_url(self):
        url = reverse('ticket_detail', kwargs={'pk':self.id})        
        return url

    def up_vote(self):
        self.votes +=1
        self.save()

    def down_vote(self):
        if self.votes > 0:
            self.votes -= 1
            self.save()
        


class UserVoteLog(models.Model):
    '''A table to keep track of which tickets a user has voted for.
    Each user can only upvote a ticket once.
    '''
    user = models.ForeignKey(User)
    ticket = models.ForeignKey(Ticket)
    
            
class FollowUp(models.Model):
    ''' '''
    ticket = models.ForeignKey(Ticket)
    parent = models.ForeignKey('self',
                                   blank=True,
                                   null=True)

    submitted_by = models.ForeignKey(User, null=True, blank=True)    
    created_on = models.DateTimeField('date created', auto_now_add=True)
    comment = models.TextField()
    closed = models.BooleanField(default=False)
    
class TicketAdmin(admin.ModelAdmin):
    date_heirarchy = "created_on"
    list_filter = ("status",)
    list_display = ("id", "name", "status", "assigned_to")
    search_field = ['description']

admin.site.register(Ticket, TicketAdmin)
