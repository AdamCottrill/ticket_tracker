import factory
from datetime import datetime
from django.contrib.auth.models import User

from tickets.models import Ticket, FollowUp, Application


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    first_name = 'John'
    last_name = 'Doe'
    username = factory.Sequence(lambda n: "johndoe{}".format(n))
    email = 'johndoe@hotmail.com'
    password = 'Abcdef12'
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class ApplicationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Application
        django_get_or_create = ('slug',)

    application = "MyFakeApp"
    slug = "myfakeapp"

class TicketFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Ticket

    title = 'This is my ticket title'
    submitted_by = factory.SubFactory(UserFactory)
    application = factory.SubFactory(ApplicationFactory)
    status = 'new'
    ticket_type = 'bug'
    description = 'There is something wrong.'
    priority = 3
    created_on = datetime.now()
    parent = None
    active = True


class FollowUpFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = FollowUp

    ticket = factory.SubFactory(TicketFactory)
    submitted_by = factory.SubFactory(UserFactory)
    comment = "Ok - we will take a look at it"
    private = False
