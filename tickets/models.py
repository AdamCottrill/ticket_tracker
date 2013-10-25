from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse



class TicketManager(models.Manager):
    '''A custom model manager for tickets'''

    def get_query_set(self):        
        '''only those tickets that are active'''
        #return self.filter(active=True)
        return super(TicketManager, self).get_query_set().filter(active=True)
    

class CommentManager(models.Manager):
    '''A custom model manager for comments'''

    def get_query_set(self):
        '''only those comments that are not private'''
        #return self.filter(private=False)
        return super(CommentManager, self).get_query_set().filter(private=False)
            
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
        ('split', 'Closed - Split'),            
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
    active = models.BooleanField(default=True)
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

    all_tickets = models.Manager()
    objects = TicketManager()
    
    def __unicode__(self):
        name = self.description.split("\n", 1)[0]
        name = name[:30]
        return name
    
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

    def duplicate_of(self, original_pk):
        '''a method to flag this ticket as a duplicate of another.
        Automatically created an appropriate record in TicketDuplicate
        table.
        '''
        original = Ticket.objects.get(pk=original_pk)
        duplicate = TicketDuplicate(ticket=self, original=original)
        duplicate.save()

    def get_duplicates(self):
        '''a method to retreive all of the ticket objects that have
        been flagged as duplicates of this ticket.
        '''
        duplicates = TicketDuplicate.objects.filter(original=self)
        if not duplicates:
            duplicates = None
        return duplicates


    def get_originals(self):
        '''a method to retreive the ticket object that this ticket
        duplicates.
        '''
        originals = TicketDuplicate.objects.filter(ticket=self)
        if not originals:
            originals = None
        return originals

    def get_parent(self):
        '''a method to return the ticket that this ticket was split
        out of
        '''
        if self.parent:
            try:
                parent = Ticket.objects.get(id=self.parent.id)
            except Ticket.DoesNotExist:
                parent = None
        else:
            parent = None
        return parent
        
    def get_children(self):
        '''return any tickets that were create by splitting this
        ticket
        '''
        children = Ticket.objects.filter(parent=self.id)
        if not children:
            children = None
        return children
        
    def is_closed(self):
        '''a boolean method to indicate if this ticket is open or
        closed.  Makes templating much simpler.
        '''
        if self.status in ('closed', 'duplicate', 'split'):
            return True
        else:
            return False
        

class TicketDuplicate(models.Model):
    '''A simple table to keep track of which tickets are duplicates of
    which ticket.

    '''
    ticket = models.ForeignKey(Ticket,related_name="duplicate")
    original = models.ForeignKey(Ticket,related_name="original")
    
    def __unicode__(self):
        string = "Ticket {0} is a duplicate of ticket {1}"
        string = string.format(self.ticket.id, self.original.id)
        return string
            

class UserVoteLog(models.Model):
    '''A table to keep track of which tickets a user has voted for.
    Each user can only upvote a ticket once.
    '''
    user = models.ForeignKey(User)
    ticket = models.ForeignKey(Ticket)
    
            
class FollowUp(models.Model):
    ''' '''

    ACTION_CHOICES = {
        ('no_action', 'No Action'),
        ('closed', 'Closed'),
        ('reopened', 'Re-Opened'),
        ('split', 'Split')        
    }
    
    ticket = models.ForeignKey(Ticket)
    parent = models.ForeignKey('self',
                                   blank=True,
                                   null=True)

    submitted_by = models.ForeignKey(User, null=True, blank=True)    
    created_on = models.DateTimeField('date created', auto_now_add=True)
    comment = models.TextField()
    #closed = models.BooleanField(default=False)
    action = models.CharField(max_length=20, 
                              choices=ACTION_CHOICES, default="no_action")
    private = models.BooleanField(default=False)

    objects = CommentManager()
    all_comments = models.Manager()

    
class TicketAdmin(admin.ModelAdmin):
    date_heirarchy = "created_on"
    list_filter = ("status",)
    list_display = ("id", "name", "status", "assigned_to")
    search_field = ['description']

admin.site.register(Ticket, TicketAdmin)
