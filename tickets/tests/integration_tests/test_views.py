import unittest

from django.conf import settings
#from django.contrib.auth.models import User, Group
#from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase


from tickets.tests.factories import *


class TicketTestCase(TestCase):
    ''' '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticekt = TicketFactory()
        
    def test_ticket_detail(self):        

        pass
        ##login = self.client.login(username=self.user.username, password='abc')
        ##self.assertTrue(login)
        ##response = self.client.get(reverse('MyProjects'),follow=True) 
        ##self.assertEqual(response.status_code, 200)
        ##self.assertTemplateUsed(response, "my_projects.html")
        ##self.assertContains(response, 'Bookmarks')
        

    def test_ticket_update_not_logged_in(self):        
        '''user's who aren't logged in should not be able to edit
        tickets.
        '''
        pass
        ## login = self.client.login(username=self.user.username, password='abc')
        ## self.assertTrue(login)
        ## response = self.client.get(reverse('MyProjects'),follow=True) 
        ## self.assertEqual(response.status_code, 200)
        ## self.assertTemplateUsed(response, "my_projects.html")
        ## self.assertContains(response, 'Bookmarks')
        

    def test_ticket_update_not_owner(self):        
        '''user's who aren't the ticket owner or administrator should
        not be able to edit the tickets.
        '''
        pass

    def test_ticket_update_owner(self):        
        '''the ticket's owner should be able to edit the ticket.
        '''
        pass
        
    def test_ticket_update_admin(self):        
        '''user's who aren't logged in should not be able to edit
        tickets.
        '''
        pass
        
        
class TicketListTestCase(TestCase):
    '''There are a number of views that present various subsets of
    ticket in list form - verify that those lists contain the
    appropriate tickets

    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticekt = TicketFactory()
        
    def test_ticket_list(self):        
        '''this view should return all of our tickets'''
        pass

    def test_my_tickets_list(self):        
        '''this view should return only those tickets that belong to
        our user
        '''
        pass

    def test_open_ticket_list(self):        
        '''this view should return only those tickets that are currenly opened.
        It should not include any tickets that are closed, duplicate or split
        '''
        pass

    def test_closed_ticket_list(self):        
        '''this view should return only those tickets that have been
        closed.  this will include only tickets that are closed,
        duplicate or split
        '''
        pass


    def test_bug_ticket_list(self):        
        '''this view should return only those tickets that are bug
        reports.  No feature request tickets should appear in this
        response.
        '''
        pass


    def test_feature_reqeust_list(self):        
        '''this view should return only those tickets that are bug
        reports.  No feature request tickets should appear in this
        response.
        '''
        pass


        
class TicketUpdateTestCase(TestCase):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticekt = TicketFactory()

        
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
        self.ticekt = TicketFactory()

        
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
        self.ticekt = TicketFactory()

        
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

        self.user = UserFactory()
        self.ticekt = TicketFactory()

        
    def test_vote_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to vote for a
        ticket
        '''
        pass
        
    def test_vote_logged_in(self):
        '''if you're  logged in you should be able to vote for a
        ticket once 
        '''
        pass
        
    def test_vote_twice_logged_in(self):
        '''you can only vote for ticket once.
        '''
        pass
        