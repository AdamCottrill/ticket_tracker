
from django_webtest import WebTest

from tickets.tests.factories import *


class TicketUpdateTestCase(WebTest):
    '''
    '''

    def setUp(self):        

        self.user = UserFactory()
        self.user2 = UserFactory(is_staff=True)
        self.user3 = UserFactory(username='hsimpson')
        
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
        self.user2 = UserFactory(is_staff=True)
        self.user3 = UserFactory(username='hsimpson')

        self.ticket = TicketFactory()
        self.ticket2 = TicketFactory(description='This is a duplicate')
        
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
        login = self.client.login(username=self.user.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('comment_ticket', 
                      kwargs=({'pk':self.ticket.id}))
        response = self.app.get(url, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        form['comment'] = 'What a great idea'

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response,'What a great idea')

    def test_close_ticket_admin(self):
        '''if you're an administator, you should be able to close a
        ticket
        '''        

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('close_ticket', 
                      kwargs=({'pk':self.ticket.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        form['comment'] = 'This feature has been implemented'
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response,'This feature has been implemented')

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.status,'closed')

        
    def test_close_ticket_non_admin(self):
        '''if you're an not administator, you should NOT be able to close a
        ticket
        '''
        pass
        
    def test_reopen_ticket_admin(self):
        '''if you're an administator, you should be able to reopen a
        ticket
        '''

        #make sure that the ticket is closed before we do anything
        self.ticket = Ticket.objects.get(id=self.ticket.id)
        self.ticket.status = 'closed'
        self.ticket.save()
        self.assertEqual(self.ticket.status,'closed')

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('reopen_ticket', 
                      kwargs=({'pk':self.ticket.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        msg = 'This ticket needs to be reopened'
        form['comment'] = msg
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response,msg)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.status,'reopened')

        
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

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('close_ticket', 
                      kwargs=({'pk':self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['duplicate'].checked = True
        form['same_as_ticket'] = 1
        
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        #verify that the message appears in the response:
        self.assertContains(response,msg)
        self.assertContains(response,'This ticket duplicates ticket(s):')
        #check that the status of ticket 2 has been updated
        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status,'duplicate')

        #get the original ticket for ticket 2 and verify that it is ticket 1
        original = ticket.get_originals()
        self.assertEqual(self.ticket, original[0].original)


        
    def test_close_ticket_as_duplicate_to_self(self):
        '''If the ticket number entered in same_as_ticket is the same
        as the current ticket, the form should throw an error

        '''
        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('close_ticket', 
                      kwargs=({'pk':self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['duplicate'].checked = True
        form['same_as_ticket']=2 #WRONG
        
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        errmsg = "Invalid ticket number. A ticket cannot duplicate itself."
        self.assertContains(response,msg)
        self.assertContains(response,errmsg)
        
        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status,'new')


        
    def test_close_ticket_as_duplicate_missing_ticket(self):
        '''If you forget to provide a duplicate ticket, the form
        should throw an error

        '''

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('close_ticket', 
                      kwargs=({'pk':self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['duplicate'].checked = True
        
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        errmsg = "Duplicate true, no ticket number provided."
        self.assertContains(response,msg)
        self.assertContains(response,errmsg)
        
        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status,'new')


        
    def test_close_ticket_as_duplicate_missing_check(self):
        '''If you forget to check the duplicate box but provide a
        number, the form should throw an error

        '''
        # verify that a comment was created and that the status of the
        # original ticket has been updated accordingly

        pass

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)
        
        url = reverse('close_ticket', 
                      kwargs=({'pk':self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        
        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['same_as_ticket']=1
        
        response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        errmsg = "Duplicate false, ticket number provided."
        self.assertContains(response,msg)
        self.assertContains(response,errmsg)

        #verify that the status of ticket2 has not been changed.
        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status,'new')
        
        
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
        