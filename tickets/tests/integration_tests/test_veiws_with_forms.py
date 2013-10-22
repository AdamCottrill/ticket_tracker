
from django_webtest import WebTest

from tickets.tests.factories import *


class TicketUpdateTestCase(WebTest):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.user2 = UserFactory(is_staff=True)
        self.user3 = UserFactory(username='hsimpson',
                                 is_staff=False)
        
        self.status = 'new'
        self.ticket_type = 'bug'
        self.description = 'There is something wrong.'
        self.priority = 3
        
        self.ticket = TicketFactory(submitted_by=self.user,
                                    status=self.status,
                                    ticket_type=self.ticket_type,
                                    description = self.description,
                                    priority=self.priority)
        
    def test_update_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to edit a
        ticket
        '''
        url = reverse('update_ticket', 
                      kwargs=({'pk':self.ticket.id}))

        response = self.app.get(url).follow()
        location = response['Location']
        new_url = '{0}?next={1}'.format(reverse('login'), url)
        self.assertEqual(response.status_code, 301)        
        self.assertIn(new_url, location)

    def test_update_logged_not_owner(self):
        '''if you're not the ticket's owner you shouldn't be able to edit a
        ticket
        '''
        login = self.client.login(username=self.user3.username,
                                  password='Abcdef12')
        
        self.assertTrue(login)
        url = reverse('update_ticket', 
                      kwargs=({'pk':self.ticket.id}))
        response = self.app.get(url, user=self.user3).follow()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        
    def test_update_logged_owner(self):
        '''if you're the ticket's owner you should be able to edit the
        ticket
        '''

        login = self.client.login(username=self.user.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('update_ticket', 
                      kwargs=({'pk':self.ticket.id}))
        response = self.app.get(url, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_form.html')
        
        form = response.forms['ticket']

        form['status'] = 'accepted'
        form['ticket_type'] = 'feature'
        form['description'] = "Nevermind it is OK."
        form['priority'] = 4

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        
        self.assertContains(response, 'Accepted')
        self.assertContains(response, 'Feature Request')        
        self.assertContains(response, "Nevermind it is OK.")

    def test_update_logged_admin(self):
        '''if you're an administator, you should be able to edit the
        ticket even if you didn't create it.
        '''
        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('update_ticket', 
                      kwargs=({'pk':self.ticket.id}))
        response = self.app.get(url, user=self.user)
        print "response = %s" % response

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_form.html')
        
        form = response.forms['ticket']

        form['status'] = 'accepted'
        form['ticket_type'] = 'feature'
        form['description'] = "Nevermind it is OK."
        form['priority'] = 4

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        
        self.assertContains(response, 'Accepted')
        self.assertContains(response, 'Feature Request')        
        self.assertContains(response, "Nevermind it is OK.")
        

class SplitTicketTestCase(WebTest):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticket = TicketFactory()
        
    def test_split_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to split a
        ticket
        '''
        url = reverse('split_ticket', 
                      kwargs=({'pk':self.ticket.id}))

        response = self.app.get(url).follow()
        location = response['Location']
        new_url = '{0}?next={1}'.format(reverse('login'), url)
        self.assertEqual(response.status_code, 301)        
        self.assertIn(new_url, location)

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

        


class TicketFollowupTestCase(WebTest):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.ticket = TicketFactory()
        
    def test_comment_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to comment on
        a ticket
        '''
        url = reverse('comment_ticket', 
                      kwargs=({'pk':self.ticket.id}))

        response = self.app.get(url).follow()
        location = response['Location']
        new_url = '{0}?next={1}'.format(reverse('login'), url)
        
        self.assertEqual(response.status_code, 301)        
        self.assertIn(new_url, location)


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
        