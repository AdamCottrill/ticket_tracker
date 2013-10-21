import unittest

from django.conf import settings
#from django.contrib.auth.models import User, Group
#from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase


from tickets.tests.factories import *


class TicketTestCase(TestCase):
    '''Verify that the ticket detail view renders all of the required
    information inlcuding links to parent and child tickets as well as
    any duplicates/original.
    '''

    def setUp(self):        

        self.user = UserFactory()
        desc = 'This is the first ticket'
        self.ticket = TicketFactory(submitted_by=self.user,
                                    description=desc)
        
        desc = 'This is a duplicate of ticket1'
        self.ticket2 = TicketFactory(description=desc)
        
        desc = 'This will be the 1st child of ticket1'
        self.ticket3 = TicketFactory(submitted_by=self.user,
                                     description=desc,
                                     parent=self.ticket)
        
        #flag ticket 2 as a duplicate of the first
        self.ticket2.duplicate_of(self.ticket.id)

        
    def test_ticket_detail(self):        
        '''make sure that all of the relevant details appear on the
        basic detail page
        '''
        
        url = reverse('ticket_detail', kwargs={'pk':self.ticket.id})
        response = self.client.get(url,follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_detail.html")
        self.assertContains(response, self.ticket.description)
        self.assertContains(response, self.ticket.priority)
        self.assertContains(response, self.ticket.votes)
        self.assertContains(response, self.user.username)

        self.assertContains(response, 'Priority:')
        self.assertContains(response, 'Opened:')
        self.assertContains(response, 'Last modified:')                        
        self.assertContains(response, 'Submitted by:')
        self.assertContains(response, 'Assigned to:')
        self.assertContains(response, 'Comments:')                        

        self.assertNotContains(response, 'Parent Ticket:')
        

    def test_ticket_detail_includes_parent_id(self):        
        '''if a ticket has a parent, make sure that the view includes
        a link back to its parent
        '''

        #ticket ticket is the parent of ticket 1
        url = reverse('ticket_detail', kwargs={'pk':self.ticket3.id})
        response = self.client.get(url,follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_detail.html")

        self.assertContains(response, 'Parent Ticket')
        #there should be a link to the parent ticket in the response
        url = reverse('ticket_detail', kwargs={'pk':self.ticket.id})
        linktext ='<a href="{0}">{1}... (ticket #{2})</a>'
        linktext = linktext.format(url, self.ticket, self.ticket.id)

        self.assertContains(response, linktext, html=True)

    def test_ticket_detail_includes_child_info(self):        
        '''if a ticket has a child, make sure that the view includes
        a link back to its the child
        '''
        #ticket ticket is the parent of ticket 1
        url = reverse('ticket_detail', kwargs={'pk':self.ticket.id})
        response = self.client.get(url,follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_detail.html")

        self.assertContains(response, 'Child Ticket(s)')
        #there should be a link to the child ticket in the response
        url = reverse('ticket_detail', kwargs={'pk':self.ticket3.id})
        linktext ='<a href="{0}">{1} (ticket #{2})</a>'
        linktext = linktext.format(url, self.ticket3, self.ticket3.id)
        self.assertContains(response, linktext, html=True)
        

    def test_ticket_detail_duplicate_id(self):        
        '''if a ticket has duplicates associated with it, make sure
        that the view includes a linke back to them.
        '''
        
        # ticket had has a duplicate 
        url = reverse('ticket_detail', kwargs={'pk':self.ticket.id})
        response = self.client.get(url,follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_detail.html")

        self.assertContains(response,
                            'This ticket has been duplicated by')

        #there should be a link to the duplicate ticket in the response
        url = reverse('ticket_detail', kwargs={'pk':self.ticket2.id})
        linktext ='<a href="{0}">{1} (ticket #{2})</a>'
        linktext = linktext.format(url, self.ticket2, self.ticket2.id)
        self.assertContains(response, linktext, html=True)
        


    def test_ticket_detail_original_id(self):        
        '''if a ticket has been flagged as a duplicate, make sure that
        the view includes a link back to the orginal ticket
        '''
        #this ticket has been flagged as a duplicate
        url = reverse('ticket_detail', kwargs={'pk':self.ticket2.id})
        response = self.client.get(url,follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_detail.html")

        self.assertContains(response,
                            'This ticket duplicates ticket(s):')

        #there should be a link to the child ticket in the response
        url = reverse('ticket_detail', kwargs={'pk':self.ticket.id})
        linktext ='<a href="{0}">{1} (ticket #{2})</a>'
        linktext = linktext.format(url, self.ticket, self.ticket.id)
        self.assertContains(response, linktext, html=True)

        
class TicketListTestCase(TestCase):
    '''There are a number of views that present various subsets of
    ticket in list form - verify that those lists contain the
    appropriate tickets
    '''

    def setUp(self):        

        self.user1 = UserFactory(first_name='Homer',
                                 last_name='Simpson')

        desc = "This ticket is new. findme."
        self.ticket1 = TicketFactory(status='new',
                                     submitted_by=self.user1,
                                     ticket_type='feature',
                                     description=desc)
        
        self.ticket2 = TicketFactory(status='accepted',
                                     submitted_by=self.user1,
                                     description="This ticket is accepted.")
        
        self.ticket3 = TicketFactory(status='assigned',
                                     ticket_type='feature',
                                     description="This ticket is assigned.")

        desc = "This ticket is reopened. findme."
        self.ticket4 = TicketFactory(status='reopened',
                                     description=desc)

        desc = "This ticket is closed. findme"
        self.ticket5 = TicketFactory(status='closed',
                                     description=desc)

        self.ticket6 = TicketFactory(status='duplicate',
                                     description="This ticket is a duplicate.")

        self.ticket7 = TicketFactory(status='split',
                                     description="This ticket is split.")

        #TODO - activate for inactive:
        #self.ticket8 = TicketFactory(active=False)                        

    def test_ticket_list(self):        
        '''this view should return all of our tickets'''

        url = (reverse('ticket_list'))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        self.assertContains(response, self.ticket1.name())
        self.assertContains(response, self.ticket2.name())
        self.assertContains(response, self.ticket3.name())
        self.assertContains(response, self.ticket4.name())                
        self.assertContains(response, self.ticket5.name())
        self.assertContains(response, self.ticket6.name())
        self.assertContains(response, self.ticket7.name())        

    def test_ticket_list_with_q(self):        
        '''this view should return all of our tickets that contain q
        in their desciption
        '''
        q = 'findme'
        url = (reverse('ticket_list'))
        response = self.client.get(url, {'q':q}, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

        #only tickets contain the string 'findme'
        self.assertContains(response, self.ticket1.name())
        self.assertContains(response, self.ticket4.name())                
        self.assertContains(response, self.ticket5.name())

        self.assertNotContains(response, self.ticket2.name())
        self.assertNotContains(response, self.ticket3.name())
        self.assertNotContains(response, self.ticket6.name())
        self.assertNotContains(response, self.ticket7.name())        
        
    def test_my_tickets_list(self):        
        '''this view should return only those tickets that belong to
        our user
        '''
        url = (reverse('my_ticket_list',
                       kwargs={'userid':self.user1.id}))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

        #ticket 1 and 2 were created by homer:
        self.assertContains(response, self.ticket1.name())
        self.assertContains(response, self.ticket2.name())
        #these were not:
        self.assertNotContains(response, self.ticket3.name())
        self.assertNotContains(response, self.ticket4.name())                
        self.assertNotContains(response, self.ticket5.name())
        self.assertNotContains(response, self.ticket6.name())
        self.assertNotContains(response, self.ticket7.name())        

    def test_my_tickets_list_with_q(self):        
        '''this view should return only those tickets that belong to
        our user and contain the string contained in q

        NOTE - this view exists, but there is currenly no way to
        access this view from out existing user interface.
        '''
        
        q = 'findme'
        url = (reverse('my_ticket_list',
                       kwargs={'userid':self.user1.id}))
        response = self.client.get(url,{'q':q}, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

        #only ticket 1 was created by homer and contain 'findme'
        self.assertContains(response, self.ticket1.name())

        #these were not created by homer or do not contain 'findme':
        self.assertNotContains(response, self.ticket2.name())
        self.assertNotContains(response, self.ticket3.name())
        self.assertNotContains(response, self.ticket4.name())                
        self.assertNotContains(response, self.ticket5.name())
        self.assertNotContains(response, self.ticket6.name())
        self.assertNotContains(response, self.ticket7.name())        


    def test_my_tickets_list_nonexistant_user(self):        
        '''this view should return all tickets since the user with id
        22 does not exist

        '''
        url = (reverse('my_ticket_list', kwargs={'userid':22}))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        self.assertContains(response, self.ticket1.name())
        self.assertContains(response, self.ticket2.name())
        self.assertContains(response, self.ticket3.name())
        self.assertContains(response, self.ticket4.name())                
        self.assertContains(response, self.ticket5.name())
        self.assertContains(response, self.ticket6.name())
        self.assertContains(response, self.ticket7.name())        
                
    def test_open_ticket_list(self):        
        '''this view should return only those tickets that are currenly open.
        It should not include any tickets that are closed, duplicate or split
        '''

        url = (reverse('open_tickets'))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        self.assertContains(response, self.ticket1.name())
        self.assertContains(response, self.ticket2.name())
        self.assertContains(response, self.ticket3.name())
        self.assertContains(response, self.ticket4.name())
        
        self.assertNotContains(response, self.ticket5.name())
        self.assertNotContains(response, self.ticket6.name())
        self.assertNotContains(response, self.ticket7.name())        

    def test_closed_ticket_list(self):        
        '''this view should return only those tickets that have been
        closed.  this will include only tickets that are closed,
        duplicate or split
        '''
        url = (reverse('closed_tickets'))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        self.assertNotContains(response, self.ticket1.name())
        self.assertNotContains(response, self.ticket2.name())
        self.assertNotContains(response, self.ticket3.name())
        self.assertNotContains(response, self.ticket4.name())
        
        self.assertContains(response, self.ticket5.name())
        self.assertContains(response, self.ticket6.name())
        self.assertContains(response, self.ticket7.name())        

    def test_bug_ticket_list(self):        
        '''this view should return only those tickets that are bug
        reports.  No feature request tickets should appear in this
        response.
        '''
        #all tickest except for 1 and 3 should be bugs (default)
        
        url = (reverse('bug_reports'))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        
        self.assertNotContains(response, self.ticket1.name())
        self.assertNotContains(response, self.ticket3.name())

        self.assertContains(response, self.ticket2.name())
        self.assertContains(response, self.ticket4.name())
        self.assertContains(response, self.ticket5.name())
        self.assertContains(response, self.ticket6.name())
        self.assertContains(response, self.ticket7.name())        

    def test_feature_reqeust_list(self):        
        '''this view should return only those tickets that are bug
        reports.  No feature request tickets should appear in this
        response.
        '''
        
        url = (reverse('feature_requests'))
        response = self.client.get(url, follow=True) 
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

        #1 and 3 are the only feature requests
        self.assertContains(response, self.ticket1.name())
        self.assertContains(response, self.ticket3.name())

        self.assertNotContains(response, self.ticket2.name())
        self.assertNotContains(response, self.ticket4.name())
        self.assertNotContains(response, self.ticket5.name())
        self.assertNotContains(response, self.ticket6.name())
        self.assertNotContains(response, self.ticket7.name())        

        
class TicketUpdateTestCase(TestCase):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticket = TicketFactory()

        
    def test_update_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to edit a
        ticket
        '''
        pass

    def test_update_logged_not_owner(self):
        '''if you're not the ticket's owner you shouldn't be able to edit a
        ticket
        '''
        pass


    def test_update_logged_owner(self):
        '''if you're the ticket's owner you should be able to edit the
        ticket
        '''
        pass

    def test_update_logged_admin(self):
        '''if you're an administator, you should be able to edit the
        ticket
        '''
        pass

        

class SplitTicketTestCase(TestCase):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticket = TicketFactory()

        
    def test_split_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to split a
        ticket
        '''
        pass

    def test_split_logged_in_not_admin(self):
        '''you have to be an administrator to split tickets
        ticket
        '''
        pass

    def test_split_logged_admin(self):
        '''if you're an administator, you should be able to split a
        ticket
        '''
        # verify that a comment was created on the original ticket and
        # that the status of the original ticket has been updated
        # accordingly
        #verify that two new tickets where created
        pass

        


class TicketFollowupTestCase(TestCase):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticket = TicketFactory()

        
    def test_comment_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to comment on
        a ticket
        '''
        pass

    def test_comment_logged_in_not_admin(self):
        '''you don't have to be an admin to comment on a ticket - just
        logged in
        '''
        pass

    def test_close_ticket_admin(self):
        '''if you're an administator, you should be able to close a
        ticket
        '''
        # verify that a comment was created and that the status of the
        # original ticket has been updated accordingly
        pass

    def test_close_ticket_non_admin(self):
        '''if you're an not administator, you should NOT be able to close a
        ticket
        '''
        pass

    def test_reopen_ticket_admin(self):
        '''if you're an administator, you should be able to reopen a
        ticket
        '''
        # verify that a comment was created and that the status of the
        # original ticket has been updated accordingly        
        pass

    def test_reopen_ticket_non_admin(self):
        '''if you're an not administator, you should NOT be able to reopen a
        ticket
        '''
        pass

    def test_close_ticket_as_duplicate_admin(self):
        '''if you're an administator, you should be able to close a
        ticket  as a duplicate
        '''
        # verify that a comment was created and that the status of the
        # original ticket has been updated accordingly

        pass

    def test_close_ticket_as_duplicate_non_admin(self):
        '''if you're an not administator, you should NOT be able to close a
        ticket as a duplicate
        '''
        pass

                
    def test_comment_non_existent_ticket(self):
        '''if you try to comment on an non-existent ticket, you will
        be re-directed to licket list.
        '''
        pass


        
class VotingTestCase(TestCase):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory(username = 'hsimpson',
                                password='abc')
        self.ticket = TicketFactory()

        
    def test_vote_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to vote for a
        ticket
        '''

        self.assertEqual(self.ticket.votes, 0)
        url = (reverse('upvote_ticket', kwargs={'pk':self.ticket.id}))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.ticket.votes, 0)
        
    def test_vote_logged_in(self):
        '''if you're  logged in you should be able to vote for a
        ticket once 
        '''

        login = self.client.login(username=self.user.username,
                                  password='abc')
        self.assertTrue(login)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.votes, 0)        

        url = (reverse('upvote_ticket', kwargs={'pk':self.ticket.id}))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.votes, 1)
        
    def test_vote_twice_logged_in(self):
        '''you can only vote for ticket once.
        '''

        login = self.client.login(username=self.user.username,
                                  password='abc')
        self.assertTrue(login)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.votes, 0)        

        url = (reverse('upvote_ticket', kwargs={'pk':self.ticket.id}))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.votes, 1)

        #homer tries to vote a second time for the same ticket
        url = (reverse('upvote_ticket', kwargs={'pk':self.ticket.id}))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.votes, 1)

        
        