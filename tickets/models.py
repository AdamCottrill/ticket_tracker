from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.


TICKET_STATUS_CHOICES = {
    ('new', 'New'),
    ('accepted', 'Accepted'),
    ('assigned', 'Assigned'),
    ('reopened', 'Reopened'),
    ('closed', 'Closed'),    
}

class Ticket(models.Model):
    '''
    '''
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    status = models.CharField(max_length=20, 
                              choices=TICKET_STATUS_CHOICES, default=True)
    description = models.TextField()
    created_on = models.DateTimeField('date created', auto_now_add=True)
    updated_on = models.DateTimeField('date updated', auto_now=True)

    def name(self):
        return self.description.split("\n", 1)[0]

    def get_absolute_url(self):
        return str(self.id)

class TicketAdmin(admin.ModelAdmin):
    date_heirarchy = "created_on"
    list_filter = ("status",)
    list_display = ("id", "name", "status", "assigned_to")
    search_field = ['description']

admin.site.register(Ticket, TicketAdmin)
