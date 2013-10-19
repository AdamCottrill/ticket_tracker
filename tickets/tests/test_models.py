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
        self.assertEqual(self.ticket1.get_absolute_url(),'/ticket/1/')
        self.assertEqual(self.ticket2.get_absolute_url(),'/ticket/2/')
                

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



class TestTicketParentChildren(TestCase):
    '''Verify that the ticket methods to retrieve parent and child
    tickets work as expected.

    '''
    def setUp(self):
        '''Create 4 tickets - the first will be the parent of 2 and 3.
        the fourth is unrealte and should not be returned by either
        get_parent or get_children
        '''
        self.ticket1 = TicketFactory()
        self.ticket2 = TicketFactory(parent=self.ticket1)
        self.ticket3 = TicketFactory(parent=self.ticket1)
        self.ticket4 = TicketFactory()
        
    def test_ticket_get_parent(self):
        '''verify that only ticket 2 and 3 have a parent and that it
        is ticket 1.  Ticket 4 is not a parent and has no parent.
        '''
        
        self.assertEqual(None, self.ticket1.get_parent())
        self.assertEqual(self.ticket1, self.ticket2.get_parent())
        self.assertEqual(self.ticket1, self.ticket3.get_parent())
        self.assertEqual(None, self.ticket4.get_parent())



    def test_ticket_get_parent_orphan(self):
        '''Just incase a ticket has a parent that does not, or no
        longer exists, get parent should gracefully return None

        '''
        
        self.ticket1.delete()
        self.assertEqual(None, self.ticket2.get_parent())
        self.assertEqual(None, self.ticket3.get_parent())
        

    def test_ticket_get_children(self):
        '''Only ticket 1 has children - they should be ticket 2 and ticket 3.'''
        children = self.ticket1.get_children()

        shouldbe = [self.ticket2.id,self.ticket3.id]

        self.assertQuerysetEqual(
            children, shouldbe,
            lambda a:a.id
            )

        self.assertEqual(self.ticket2.get_children(), None)
        self.assertEqual(self.ticket3.get_children(), None)
        self.assertEqual(self.ticket4.get_children(), None)
        
        
    def tearDown(self):
        #self.ticket.delete()
        pass


class TestTicketIsClose(TestCase):
    '''Verify that the ticket.is_closed method work as expected
    (returns true for closed, split, and duplicate, but false
    otherwise).

    '''
    def setUp(self):
        '''Create a for each status'''
        
        self.ticket1 = TicketFactory(status='new')
        self.ticket2 = TicketFactory(status='accepted')
        self.ticket3 = TicketFactory(status='assigned')
        self.ticket4 = TicketFactory(status='reopened')
        self.ticket5 = TicketFactory(status='closed')        
        self.ticket6 = TicketFactory(status='duplicate')
        self.ticket7 = TicketFactory(status='split')        

    def test_ticket_is_closed(self):
        '''verify that ticket.is_closed() is true tickets with status
        of closed, duplicate and split, false otherwise.
        '''

        #these should all be false
        self.assertFalse(self.ticket1.is_closed())
        self.assertFalse(self.ticket2.is_closed())
        self.assertFalse(self.ticket3.is_closed())
        self.assertFalse(self.ticket4.is_closed())
        #these should all be true
        self.assertTrue(self.ticket5.is_closed())
        self.assertTrue(self.ticket6.is_closed())
        self.assertTrue(self.ticket7.is_closed())

    def tearDown(self):
        #self.ticket.delete()
        pass



class TestTicketDuplicates(TestCase):
    '''Verify that we can create and retrieve duplicate tickets
    '''
    def setUp(self):
        '''We'll need three tickets - ticket 2 will be a duplicate of
        ticket 1.  Ticket 3 is indepent of either and should not
        appear in any of our return values.
        '''
        
        self.ticket1 = TicketFactory()
        self.ticket2 = TicketFactory()
        self.ticket3 = TicketFactory()

    def test_ticket_duplicate_of(self):
        '''verify that the ticket.duplicate_of() method creates a
        record in the TicketDuplicate table and that the ticket is the
        duplcate ticket, orginial is the parent ticket.

        '''

        self.ticket2.duplicate_of(self.ticket1.id)
        duplicates = TicketDuplicate.objects.all()
        
        self.assertEqual(duplicates[0].ticket, self.ticket2)
        self.assertEqual(duplicates[0].original, self.ticket1)


    def test_get_duplicate_and_original_tickets(self):

        #identify ticket 2 as a duplicate of ticket1
        self.ticket2.duplicate_of(self.ticket1.id)

        self.assertEqual(self.ticket2.get_originals()[0].original.id,
                         self.ticket1.id)
        self.assertEqual(self.ticket1.get_duplicates()[0].ticket.id,
                         self.ticket2.id)

        self.assertEqual(self.ticket3.get_originals(), None)
        self.assertEqual(self.ticket3.get_duplicates(), None)
        
        
    def tearDown(self):
        #self.ticket.delete()
        pass
        