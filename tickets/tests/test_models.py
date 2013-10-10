from django.test import TestCase

from tickets.models import *
from tickets.tests.factories import *


class TestTicket(TestCase):
    '''verify that the get_url, and voting methods work as
       expected'''
    def setUp(self):

        self.name1 = '''this is short name.'''
        self.name2 = '''this is a long, one line name that should cropped.'''
        self.name3 = '''this is a long, two line name that should cropped.
        Here is the second line.'''

        
        
        self.ticket1 = TicketFactory()
        self.ticket2 = TicketFactory()

    def test_ticket_get_url(self):
        '''the url should be the primary of the object returned as a
        string
        '''
        self.assertEqual(self.ticket1.get_absolute_url(),'/ticket/1/')
        self.assertEqual(self.ticket2.get_absolute_url(),'/ticket/2/')



    def test_ticket_name(self):
        '''the name of the ticket should be the first line of the
        description, upto a maximum of 40 characters.
        '''

        
        

    def test_ticket_vote(self):
        '''verify that up_vote and down_vote method increment and
        decrement the votes associated with a ticket (but do not
        affect other active tickets)
        '''
        
        self.assertEqual(self.ticket1.votes, 0)
        self.assertEqual(self.ticket2.votes, 0)

        self.ticket1.up_vote()
        self.assertEqual(self.ticket1.votes, 1)
        self.assertEqual(self.ticket2.votes, 0)

        self.ticket1.up_vote()
        self.assertEqual(self.ticket1.votes, 2)
        self.assertEqual(self.ticket2.votes, 0)

        self.ticket1.down_vote()
        self.assertEqual(self.ticket1.votes, 1)
        self.assertEqual(self.ticket2.votes, 0)
        
        
    def tearDown(self):
        #self.ticket.delete()
        pass


class TestTicketName(TestCase):
    '''verify that the name returned by a ticket is no more than the
    first 40 characters of its discription.

    '''
    def setUp(self):

        self.name1 = '''this is a short name.'''
        self.name2 = '''this is a long, one line name that should cropped{0}.'''
        self.name2 = self.name2.format("e"*20)
        self.name3 = '''this is a long, two line name that should cropped{0}.
        Here is the second line.'''
        self.name3 = self.name3.format("e"*20)
        self.name4 = '''This is a short, two line name.
        Here is the second line.'''
        
        self.ticket1 = TicketFactory(description=self.name1)
        self.ticket2 = TicketFactory(description=self.name2)
        self.ticket3 = TicketFactory(description=self.name3)
        self.ticket4 = TicketFactory(description=self.name4)
        
    def test_ticket_name(self):
        '''the name of the ticket should be the first line of the
        description, upto a maximum of 40 characters.
        '''
        shouldbe = self.name1
        self.assertEqual(self.ticket1.name(), shouldbe)
        
        shouldbe = self.name2[:60]
        self.assertEqual(self.ticket2.name(), shouldbe)
        self.assertEqual(len(self.ticket2.name()), 60)

        shouldbe = self.name3.split('\n')[0][:60]
        self.assertEqual(self.ticket3.name(), shouldbe)

        shouldbe = self.name4.split('\n')[0]
        self.assertEqual(self.ticket4.name(), shouldbe)        

        
    def tearDown(self):
        #self.ticket.delete()
        pass
