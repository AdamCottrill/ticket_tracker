import factory
from datetime import datetime
from django.contrib.auth.models import User


from tickets.models import *


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    first_name = 'John'
    last_name = 'Doe'
    username = factory.Sequence(lambda n : "johndoe {}".format(n))
    email = 'johndoe@hotmail.com'    
    password = 'Abcdef12'
    is_active = True
    
    #from:
    #http://www.rkblog.rk.edu.pl/w/p/using-factory-boy-django-application-tests/
    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.raw_password = password            
            user.set_password(password)
            if create:
                user.save()
        return user


class TicketFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Ticket

    submitted_by = factory.SubFactory(UserFactory)
    status = 'new'
    ticket_type = 'bug'
    description = 'There is something wrong.'
    priority = 3
    created_on = datetime.now()
    parent = None

class FollowUpFactory(factory.DjangoModelFactory):
    FACTORY_FOR = FollowUp

    ticket = factory.SubFactory(TicketFactory)
    submitted_by = factory.SubFactory(UserFactory)
    comment = "Ok - we will take a look at it"



