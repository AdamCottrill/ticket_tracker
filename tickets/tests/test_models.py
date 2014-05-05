from django.test import TestCase

from tickets.models import *
from tickets.tests.factories import *

import pytest


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

        url = '/ticket/{0}/'.format(self.ticket1.id)
        self.assertEqual(self.ticket1.get_absolute_url(), url)
        url = '/ticket/{0}/'.format(self.ticket2.id)
        self.assertEqual(self.ticket2.get_absolute_url(), url)

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
        self.name2 = '''this is a long, one line name that should cropped{}.'''
        self.name2 = self.name2.format("e"*20)
        self.name3 = '''this is a long, two line name that should cropped{0}.
        Here is the second line.'''
        self.name3 = self.name3.format("e"*20)
        self.name4 = '''This is a short, two line name.
        Here is the second line.'''

        self.ticket1 = TicketFactory.build(description=self.name1)
        self.ticket2 = TicketFactory.build(description=self.name2)
        self.ticket3 = TicketFactory.build(description=self.name3)
        self.ticket4 = TicketFactory.build(description=self.name4)

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

    @pytest.mark.django_db
    def test_ticket_get_parent_orphan(self):
        '''Just incase a ticket has a parent that does not, or no
        longer exists, get parent should gracefully return None

        '''

        self.ticket1.delete()
        self.assertEqual(None, self.ticket2.get_parent())
        self.assertEqual(None, self.ticket3.get_parent())

    def test_ticket_get_children(self):
        '''Only ticket 1 has children - they should be ticket 2 and ticket
        3.'''

        children = self.ticket1.get_children()

        shouldbe = [self.ticket2.id, self.ticket3.id]

        self.assertQuerysetEqual(children, shouldbe,
                                 lambda a: a.id, ordered=False)

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

        self.ticket1 = TicketFactory.build(status='new')
        self.ticket2 = TicketFactory.build(status='accepted')
        self.ticket3 = TicketFactory.build(status='assigned')
        self.ticket4 = TicketFactory.build(status='reopened')
        self.ticket5 = TicketFactory.build(status='closed')
        self.ticket6 = TicketFactory.build(status='duplicate')
        self.ticket7 = TicketFactory.build(status='split')

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

    @pytest.mark.django_db
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


class TestTicketManager(TestCase):
    '''verify that the custom ticket manager is returning the records
       we expecte

    '''
    def setUp(self):
        '''Create some test tickets'''
        self.ticket1 = TicketFactory()
        self.ticket2 = TicketFactory()
        self.ticket3 = TicketFactory(active=False)

    def test_tickets_manager(self):
        '''we should only get active tickets with the default manager
        and all tickets with all_tickets.
        '''

        #only active tickets should be returned by the default manager
        tickets = Ticket.objects.all()
        self.assertEqual(tickets.count(), 2)
        shouldbe = [self.ticket1.id, self.ticket2.id]
        self.assertQuerysetEqual(tickets, shouldbe,
                                 lambda a: a.id, ordered=False)
        self.assertQuerysetEqual(tickets, [True, True],
                                 lambda a: a.active, ordered=False)

        #all tickets can be retrieved vy all_tickets
        tickets = Ticket.all_tickets.all()
        self.assertEqual(tickets.count(), 3)
        shouldbe = [self.ticket1.id, self.ticket2.id, self.ticket3.id]
        self.assertQuerysetEqual(tickets, shouldbe,
                                 lambda a: a.id, ordered=False)
        self.assertQuerysetEqual(tickets, [True, True, False],
                                 lambda a: a.active, ordered=False)


class TestCommentManager(TestCase):
    '''verify that the custom comment manager is returning the records
       we expect
    '''
    def setUp(self):
        '''Create some test tickets'''
        self.ticket1 = TicketFactory()

        self.comment1 = FollowUpFactory(ticket=self.ticket1)
        self.comment2 = FollowUpFactory(ticket=self.ticket1)
        self.comment3 = FollowUpFactory(ticket=self.ticket1,
                                        private=True)

    @pytest.mark.django_db
    def test_tickets_manager(self):
        '''we should only get public comments with the default manager
        and all comments with all_comments.
        '''

        #only public comments should be returned by the default manager
        comments = FollowUp.objects.all()
        self.assertEqual(comments.count(), 2)
        shouldbe = [self.comment1.id, self.comment2.id]
        self.assertQuerysetEqual(comments, shouldbe,
                                 lambda a: a.id, ordered=False)
        self.assertQuerysetEqual(comments, [False, False],
                                 lambda a: a.private, ordered=False)

        #all comments can be retrieved vy all_comments
        comments = FollowUp.all_comments.all()
        self.assertEqual(comments.count(), 3)
        shouldbe = [self.comment1.id, self.comment2.id, self.comment3.id]
        self.assertQuerysetEqual(comments, shouldbe,
                                 lambda a: a.id, ordered=False)
        self.assertQuerysetEqual(comments, [False, False, True],
                                 lambda a: a.private, ordered=False)


@pytest.mark.django_db
def test_ticket_link():
    """a simple little test to verify that the function replace_links is
    being called on ticket save and inserting the correct link into
    the ticket's html description.

    """

    desc_text = """this is similar to the problem identifed on ticket: 23"""
    ticket = TicketFactory(description=desc_text)
    ticket.save()

    link_string = '<a href="/ticket/23">ticket 23</a>'
    assert link_string in ticket.description_html


@pytest.mark.django_db
def test_comment_link():
    """a simple little test to verify that the function replace_links() is
    being called on comment save and inserting the correct to a ticket into
    the comments's html description.

    """

    desc_text = """this is similar to the problem identifed on ticket: 23"""
    comment = FollowUpFactory(comment=desc_text)
    comment.save()

    link_string = '<a href="/ticket/23">ticket 23</a>'
    assert link_string in comment.comment_html

