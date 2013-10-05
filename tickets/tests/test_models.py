from django.test import TestCase

from tickets.models import *
from tickets.tests.factories import *


class TestTicket(TestCase):
    '''verify that the get_url, and voting methods work as
       expected'''
    def setUp(self):
        self.ticket1 = TicketFactory()
        self.ticket2 = TicketFactory()

    def test_ticket_get_url(self):
        '''the url should be the primary of the object returned as a
        string
        '''
        self.assertEqual(self.ticket1.get_absolute_url(),str(1))
        self.assertEqual(self.ticket2.get_absolute_url(),str(2))


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


