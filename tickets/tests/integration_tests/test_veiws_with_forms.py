from django.contrib.auth.models import Group
from django.urls import reverse
from django_webtest import WebTest

from tickets.tests.factories import (UserFactory,
                                     TicketFactory)

from tickets.models import Ticket, FollowUp


class TicketUpdateTestCase(WebTest):
    '''
    '''

    def setUp(self):

        self.user = UserFactory(username='bsimpson',
                                first_name='Bart',
                                last_name='Simpson')
        # self.user2 = UserFactory(is_staff=True)

        self.user2 = UserFactory(username='bgumble',
                                 first_name='Barney',
                                 last_name='Gumble',
                                 is_staff=True)

        self.user3 = UserFactory(username='hsimpson',
                                 first_name='Homer',
                                 last_name='Simpson')

        adminGrp, created = Group.objects.get_or_create(name='admin')
        self.user2.groups.add(adminGrp)

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
                      kwargs=({'pk': self.ticket.id}))

        response = self.app.get(url)
        location = response['Location']
        new_url = '{0}?next={1}'.format(reverse('login'), url)
        self.assertRedirects(response, new_url)
        self.assertIn(new_url, location)

    def test_update_logged_not_owner(self):
        '''if you're not the ticket's owner you shouldn't be able to edit a
        ticket
        '''
        login = self.client.login(username=self.user3.username,
                                  password='Abcdef12')

        self.assertTrue(login)
        url = reverse('update_ticket',
                      kwargs=({'pk': self.ticket.id}))
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
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_form.html')

        # verify that the form does not contain closed, split or duplicate
        # these ticket status values are implemented else where.
        # self.assertNotContains(response, 'close') "closed" in menu!
        self.assertNotContains(response, 'split')
        self.assertNotContains(response, 'duplicate')

        form = response.forms['ticket']

        form['status'] = 'accepted'
        form['ticket_type'] = 'feature'
        form['description'] = "Nevermind it is OK."
        form['priority'] = 4

        response = form.submit().follow()

        print("response = %{}".format(response))

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
                      kwargs=({'pk': self.ticket.id}))
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

    def test_assignto_only_admin_staff(self):
        '''For now, only administrators should be eligible to assign tickets
        to.
        '''

        login = self.client.login(username=self.user.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('update_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_form.html')

        form = response.forms['ticket']

        # user2 is the only user who belongs to the admin group in this
        # test, he is the only one who should appear as an option int
        # the dropdown list, the other two should not.

        # Project Leads - should not include Barney:
        choices = form['assigned_to'].options

        choices = [x[0] for x in choices]

        assert str(self.user.id) not in choices
        assert str(self.user2.id) in choices  # the only admin.
        assert str(self.user3.id) not in choices


class SplitTicketTestCase(WebTest):
    '''
    '''

    def setUp(self):

        self.user = UserFactory(username='bsimpson',
                                first_name='Bart',
                                last_name='Simpson')

        self.user2 = UserFactory(username='bgumble',
                                 first_name='Barney',
                                 last_name='Gumble',
                                 is_staff=True)

        adminGrp, created = Group.objects.get_or_create(name='admin')
        self.user2.groups.add(adminGrp)

        self.ticket = TicketFactory()

    def test_split_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to split a
        ticket
        '''
        url = reverse('split_ticket',
                      kwargs=({'pk': self.ticket.id}))

        response = self.app.get(url)
        location = response['Location']
        new_url = '{0}?next={1}'.format(reverse('login'), url)
        self.assertRedirects(response, new_url)
        self.assertIn(new_url, location)

    def test_split_logged_in_not_admin(self):
        '''you have to be an administrator to split tickets ticket -
        if you are not an administrator, you will be re-directed to
        the tickets detail view.
        '''
        myuser = self.user
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('split_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser).follow()

        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        self.assertEqual(response.status_code, 200)


    def test_split_logged_in_admin_does_not_exsits(self):
        '''if you try to split a ticket that does not exist, you will
        be re-directed to the ticket list.

        '''
        myuser = self.user2
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('split_ticket',
                      kwargs=({'pk':999}))
        response = self.app.get(url, user=myuser).follow()

        self.assertTemplateUsed(response, 'tickets/ticket_list.html')
        self.assertEqual(response.status_code, 200)

    def test_split_logged_admin(self):
        '''if you're an administator, you should be able to split a
        ticket
        '''
        # verify that a comment was created on the original ticket and
        # that the status of the original ticket has been updated
        # accordingly
        # verify that two new tickets where created
        # TODO

        # if a ticket is assiged to someone already, assigned to is a
        # manditory field
        self.ticket.assigned_to = None

        myuser = self.user2
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('split_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser)

        self.assertTemplateUsed(response, 'tickets/split_ticket_form.html')
        self.assertEqual(response.status_code, 200)

        form = response.forms['splitticket']

        msg = 'This ticket needs to be split'
        msg1 = 'This is part 1.'
        msg2 = 'This is part 2.'

        form['comment'] = msg
        form['description1'] = msg1
        form['description2'] = msg2

        response = form.submit().follow()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        # the comment from the splitting form should be in the response
        self.assertContains(response, msg)
        msg3 = "This ticket has been split into the  following ticket(s):"
        self.assertContains(response, msg3)

        # verify that self.ticket 1 as two children and its status is split
        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.status, 'split')

        children = ticket.get_children()
        self.assertQuerysetEqual(children, [msg1, msg2],
                                 lambda a: a.__str__(), ordered=False)

    def test_split_logged_only_assingto_admin(self):
        '''if you're an administator, you should be able to split a ticket,
        but only administrators should be listed as a choice to assign
        tickets too.

        '''
        myuser = self.user2
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('split_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser)

        self.assertTemplateUsed(response, 'tickets/split_ticket_form.html')
        self.assertEqual(response.status_code, 200)

        form = response.forms['splitticket']

        # Only admin users should be on list of choices for assing_to
        choices = form['assigned_to1'].options
        choices = [x[0] for x in choices]

        assert str(self.user.id) not in choices
        assert str(self.user2.id) in choices  # the only admin.

        # Only admin users should be on list of choices for assing_to
        choices = form['assigned_to2'].options
        choices = [x[0] for x in choices]

        assert str(self.user.id) not in choices
        assert str(self.user2.id) in choices  # the only admin.


class CommentTicketTestCase(WebTest):
    '''
    '''

    def setUp(self):

        self.user = UserFactory()
        self.user2 = UserFactory(is_staff=True)
        self.user3 = UserFactory(username='hsimpson')

        adminGrp, created = Group.objects.get_or_create(name='admin')
        self.user2.groups.add(adminGrp)

        self.ticket = TicketFactory(submitted_by=self.user)

    def test_comment_non_existent_ticket(self):
        '''if we try to comment on a ticket that does not exist, we
        should be re-directed to the ticket list.

        '''

        myuser = self.user2
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('comment_ticket', kwargs=({'pk': 99}))

        response = self.app.get(url, user=myuser).follow()

        self.assertTemplateUsed(response, 'tickets/ticket_list.html')
        self.assertEqual(response.status_code, 200)

    def test_comment_not_logged_in(self):
        '''if you're not logged in you shouldn't be able to comment on
        a ticket
        '''
        url = reverse('comment_ticket',
                      kwargs=({'pk': self.ticket.id}))

        print("url = " + url)
        response = self.app.get(url)
        location = response['Location']
        new_url = '{0}?next={1}'.format(reverse('login'), url)

        self.assertRedirects(response, new_url)
        self.assertIn(new_url, location)

    def test_comment_logged_in_not_admin(self):
        '''you don't have to be an admin to comment on a ticket - just
        logged in
        '''
        login = self.client.login(username=self.user.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('comment_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']
        form['comment'] = 'What a great idea'

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response, 'What a great idea')

    def test_private_comment_logged_in_not_admin_or_creator(self):
        '''you can't leave a private comment if you are not an admin
        or the ticket creator

        '''
        myuser = self.user3
        login = self.client.login(username=myuser,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('comment_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']
        form['comment'] = 'What a great idea'

        # private should not be on of the available fields.
        self.assertNotIn('private', form.fields.keys())

    def test_private_comment_logged_in_admin(self):
        '''you can leave a private comment if you are an admin

        '''
        myuser = self.user2
        login = self.client.login(username=myuser,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('comment_ticket', kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']
        form['comment'] = 'What a great idea'
        form['private'] = True

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response, 'What a great idea')
        self.assertContains(response, 'private')

        comment = FollowUp.all_comments.filter(ticket=self.ticket)
        self.assertEqual(comment.count(), 1)
        self.assertTrue(comment[0].private)

    def test_private_comment_logged_in_creator(self):
        '''you can leave a private comment if you are the ticket
        creator

        '''
        myuser = self.user
        login = self.client.login(username=myuser,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('comment_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']
        form['comment'] = 'What a great idea'
        form['private'] = True

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response, 'What a great idea')
        self.assertContains(response, 'private')

        comment = FollowUp.all_comments.filter(ticket=self.ticket)
        self.assertEqual(comment.count(), 1)
        self.assertTrue(comment[0].private)

    def test_comment_bad_data_logged_in(self):
        '''you comment is a manditory field.  An error will be thown
        if you don't provide one.

        '''
        login = self.client.login(username=self.user.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('comment_ticket', kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=self.user)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        errmsg = "This field is required."
        self.assertContains(response, errmsg)


class CloseTicketTestCase(WebTest):
    '''
    '''

    def setUp(self):

        self.user = UserFactory()
        self.user2 = UserFactory(is_staff=True)
        self.user3 = UserFactory(username='hsimpson')

        adminGrp, created = Group.objects.get_or_create(name='admin')
        self.user2.groups.add(adminGrp)

        self.ticket = TicketFactory()
        self.ticket2 = TicketFactory(description='This is a duplicate')

    def test_close_ticket_admin(self):
        '''if you're an administator, you should be able to close a
        ticket
        '''

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('close_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']

        form['comment'] = 'This feature has been implemented'
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response, 'This feature has been implemented')

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.status, 'closed')

    def test_close_ticket_non_admin(self):
        '''if you're an not administator, you should NOT be able to close a
        ticket.  Instead, you will be re-directed to the ticket list.
        '''

        myuser = self.user
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('close_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser).follow()

        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_reopen_ticket_admin(self):
        '''if you're an administator, you should be able to reopen a
        ticket
        '''

        #make sure that the ticket is closed before we do anything
        self.ticket = Ticket.objects.get(id=self.ticket.id)
        self.ticket.status = 'closed'
        self.ticket.save()
        self.assertEqual(self.ticket.status, 'closed')

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('reopen_ticket',
                      kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']

        msg = 'This ticket needs to be reopened'
        form['comment'] = msg
        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        self.assertContains(response, msg)

        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.status, 'reopened')

    def test_reopen_ticket_non_admin(self):
        '''if you're an not administator, you should NOT be able to reopen a
        ticket.  You will be re-directed to its detail page.
        '''

        # make sure that the ticket is closed before we do anything
        self.ticket = Ticket.objects.get(id=self.ticket.id)
        self.ticket.status = 'closed'
        self.ticket.save()
        self.assertEqual(self.ticket.status, 'closed')

        myuser = self.user
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('reopen_ticket', kwargs=({'pk': self.ticket.id}))
        response = self.app.get(url, user=myuser).follow()

        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')
        self.assertEqual(response.status_code, 200)

        # make sure that the ticket is still closed
        self.ticket = Ticket.objects.get(id=self.ticket.id)
        self.ticket.status = 'closed'
        self.ticket.save()
        self.assertEqual(self.ticket.status, 'closed')

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
                      kwargs=({'pk': self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['duplicate'].checked = True
        form['same_as_ticket'] = self.ticket.id

        response = form.submit().follow()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/ticket_detail.html')

        # verify that the message appears in the response:
        self.assertContains(response, msg)
        self.assertContains(response, 'This ticket duplicates ticket(s):')
        # check that the status of ticket 2 has been updated
        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status, 'duplicate')

        # get the original ticket for ticket 2 and verify that it is ticket 1
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
                      kwargs=({'pk': self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['duplicate'].checked = True
        form['same_as_ticket'] = self.ticket2.id

        response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        errmsg = "Invalid ticket number. A ticket cannot duplicate itself."
        self.assertContains(response, msg)
        self.assertContains(response, errmsg)

        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status, 'new')

    def test_close_ticket_as_duplicate_missing_ticket(self):
        '''If you forget to provide a duplicate ticket, the form
        should throw an error

        '''

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('close_ticket',
                      kwargs=({'pk': self.ticket2.id}))
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
        self.assertContains(response, msg)
        self.assertContains(response, errmsg)

        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status, 'new')

    def test_close_ticket_as_duplicate_missing_check(self):
        '''If you forget to check the duplicate box but provide a
        number, the form should throw an error

        '''
        # verify that a comment was created and that the status of the
        # original ticket has been updated accordingly

        login = self.client.login(username=self.user2.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('close_ticket',
                      kwargs=({'pk': self.ticket2.id}))
        response = self.app.get(url, user=self.user2)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')

        form = response.forms['comment']

        msg = 'This ticket is a duplicate of an earlier ticket'
        form['comment'] = msg
        form['same_as_ticket'] = 1

        response = form.submit()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tickets/comment_form.html')
        errmsg = "Duplicate false, ticket number provided."
        self.assertContains(response, msg)
        self.assertContains(response, errmsg)

        # verify that the status of ticket2 has not been changed.
        ticket = Ticket.objects.get(id=self.ticket2.id)
        self.assertEqual(ticket.status, 'new')

    def test_close_non_existent_ticket(self):
        '''if you try to comment on an non-existent ticket, you will
        be re-directed to ticket list.
        '''

        myuser = self.user2
        login = self.client.login(username=myuser.username,
                                  password='Abcdef12')
        self.assertTrue(login)

        url = reverse('close_ticket',
                      kwargs=({'pk':999}))
        response = self.app.get(url, user=myuser).follow()

        self.assertTemplateUsed(response, 'tickets/ticket_list.html')
        self.assertEqual(response.status_code, 200)
