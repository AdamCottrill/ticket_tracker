import pytest
from datetime import datetime
from django.test import TestCase

from django.contrib.auth.models import Group

from tickets.models import *
from tickets.forms import (TicketForm, CloseTicketForm,
                           SplitTicketForm)
from tickets.tests.factories import *


class TestTicketForm(TestCase):
    '''Test the basic functionality of the ticket form'''

    def setUp(self):
        '''one ticket and one user that will be used in these tests'''
        #we need to save a user to create a valid choice
        self.user1 = UserFactory()

        adminGrp, created = Group.objects.get_or_create(name='admin')
        self.user1.groups.add(adminGrp)

        self.app = ApplicationFactory.create()
        self.ticket = TicketFactory(application=self.app)


    @pytest.mark.django_db
    def test_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = {
            'status': 'new',
            'application': 1,
            'ticket_type': 'bug',
            'description': 'this is a test',
            'priority': 3,
        }

        form = TicketForm(data=initial, instance=self.ticket)
        form.is_valid()

        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['ticket_type'], 'bug')
        self.assertEqual(form.cleaned_data['description'], 'this is a test')
        self.assertEqual(form.cleaned_data['priority'], 3)


    def test_missing_description(self):
        '''Description is a required field - the form should not be valid
        if description is omitted.
        '''

        initial = {
            'assigned_to': 1,
            'status': 'new',
            'application': 1,
            'ticket_type': 'bug',
            #'description': 'this is a test',
            'priority': 3,

        }

        form = TicketForm(data=initial, instance=self.ticket)
        self.assertFalse(form.is_valid())

    def test_missing_status(self):
        '''Status is no longer a required field as it is inferred from actions
        applied to each ticket rather than entered as a field on a form.

        '''

        initial = {
            'assigned_to': 1,
            #'status': 'new',
            'application': 1,
            'ticket_type': 'bug',
            'description': 'this is a test',
            'priority': 3,

        }

        form = TicketForm(data=initial, instance=self.ticket)
        self.assertTrue(form.is_valid())

    def test_missing_ticket_type(self):
        '''Ticket type is a required field - the form should not be valid
        if ticket type is omitted.
        '''

        initial = {
            'assigned_to':1,
            'status':'new',
            #'ticket_type':'bug',
            'description':'this is a test',
            'priority':3,
        }

        form = TicketForm(data=initial, instance=self.ticket)
        self.assertFalse(form.is_valid())


    def tearDown(self):
        pass


##class TestCommentForm(TestCase):
##
##    def setUp(self):
##
##        self.user = UserFactory()
##        self.ticket = TicketFactory.build(submitted_by=self.user)
##        self.comment = FollowUpFactory.build(ticket=self.ticket)
##
##    @pytest.mark.django_db
##    def test_good_data(self):
##        '''verify that the same data comes out as went in'''
##
##        initial = { 'comment':"A valid comment"}
##
##        form = CommentForm(data=initial, instance=self.comment,
##                           ticket=self.ticket, user=self.user)
##        self.assertTrue(form.is_valid())
##        #check the data
##        self.assertEqual(form.cleaned_data['comment'],
##                         'A valid comment')
##        self.assertFalse(form.cleaned_data['private'])
##
##    @pytest.mark.django_db
##    def test_good_data_private(self):
##        '''verify that the same data comes out as went in, including
##        the private flag
##
##        '''
##
##        initial = { 'comment':"A valid comment",
##                    'private':True}
##
##        form = CommentForm(data=initial, instance=self.comment,
##                           ticket=self.ticket, user=self.user)
##        self.assertTrue(form.is_valid())
##        #check the data
##        self.assertEqual(form.cleaned_data['comment'],
##                         'A valid comment')
##        self.assertTrue(form.cleaned_data['private'])
##
##    @pytest.mark.django_db
##    def test_missing_comment(self):
##        '''comment is a required field, verify that the form will not
##        validate without it.
##        '''
##
##        initial = { 'comment':None}
##        form = CommentForm(data=initial, instance=self.comment,
##                                   ticket=self.ticket, user=self.user)
##        self.assertFalse(form.is_valid())
##


class TestCloseTicketForm(TestCase):

    def setUp(self):

        self.user = UserFactory()
        self.comment = FollowUpFactory()
        self.ticket = TicketFactory()
        self.ticket2 = TicketFactory()


    def test_duplicate_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = { 'comment':"A valid comment"}
        form = CloseTicketForm(data=initial, instance=self.comment,
                           action='closed', ticket=self.ticket, user=self.user)
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')

    @pytest.mark.django_db
    def test_duplicate_good_ticket(self):
        '''verify that the same data comes out as went in - duplicate
        is checked and a valid ticket number
        '''

        initial = { 'comment':"A valid comment",
                    'duplicate':True,
                    'same_as_ticket': self.ticket2.id}

        form = CloseTicketForm(data=initial,
                               instance=self.comment,
                               action='closed', ticket=self.ticket,
                               user=self.user)

        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')
        self.assertTrue(form.cleaned_data['duplicate'])
        self.assertEqual(form.cleaned_data['same_as_ticket'], self.ticket2.id)


    def test_duplicate_missing_comment(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''

        initial = { 'comment':None}
        form = CloseTicketForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user,
                           action='closed')
        self.assertFalse(form.is_valid())


    def test_duplicate_missing_ticket(self):
        '''form is not valid if duplicate is checked but no ticket
        number is provided.
        '''

        initial = { 'comment':'This is a valid comment',
                    'duplicate':True}
        form = CloseTicketForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user,
                           action='closed')

        self.assertFalse(form.is_valid())

    def test_duplicate_bad_ticket(self):
        '''form is not valid if ticket number is for a ticket that doesn't exist
        '''

        initial = { 'comment':'This is a valid comment',
                    'duplicate':True, 'same_as_ticket':99}
        form = CloseTicketForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user,
                           action='closed')
        self.assertFalse(form.is_valid())


    def test_duplicate_non_numeric_ticket(self):
        '''form is not valid if ticket number is not an integer
        '''

        initial = { 'comment':'This is a valid comment',
                    'duplicate':True, 'same_as_ticket':'abc'}
        form = CloseTicketForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user,
                           action='closed')
        self.assertFalse(form.is_valid())



    def test_duplicate_missing_check(self):
        '''throw an error if a ticket number is provided but the
        duplicate check box if left blank.
        '''

        initial = { 'comment':'This is a valid comment', 'duplicate':False,
                    'same_as_ticket':1}

        form = CloseTicketForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user,
                           action='closed')
        self.assertFalse(form.is_valid())


    def tearDown(self):
        pass


class TestSplitForm(TestCase):

    def setUp(self):

        self.user = UserFactory()
        self.app = ApplicationFactory.create()
        self.ticket = TicketFactory(application=self.app)


    @pytest.mark.django_db
    def test_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = {
            'status1': 'new',
            'ticket_type1': self.ticket.ticket_type,
            'priority1': self.ticket.priority,
            'application1':  self.app.id,
            'assigned_to1': self.ticket.assigned_to,
            'description1': self.ticket.description,
            'status2': 'new',
            'ticket_type2': self.ticket.ticket_type,
            'priority2': self.ticket.priority,
            'application2':  self.app.id,
            'assigned_to2': self.ticket.assigned_to,
            'description2': self.ticket.description,
            'comment': 'This is a test',
        }

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)

        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['status1'],'new')
        self.assertEqual(form.cleaned_data['ticket_type1'],
                                           str(self.ticket.ticket_type))
        self.assertEqual(form.cleaned_data['priority1'],
                         str(self.ticket.priority))
        self.assertEqual(form.cleaned_data['assigned_to1'],
                         self.ticket.assigned_to)

        self.assertEqual(form.cleaned_data['application1'],
                         self.ticket.application)
        self.assertEqual(form.cleaned_data['application2'],
                         self.ticket.application)


        self.assertEqual(form.cleaned_data['description1'],
                         self.ticket.description)
        self.assertEqual(form.cleaned_data['status2'],'new')
        self.assertEqual(form.cleaned_data['ticket_type2'],
                         str(self.ticket.ticket_type))
        self.assertEqual(form.cleaned_data['priority2'],
                         str(self.ticket.priority))
        self.assertEqual(form.cleaned_data['assigned_to2'],
                         self.ticket.assigned_to)
        self.assertEqual(form.cleaned_data['description2'],
                         self.ticket.description)

        #save the form and verify the effects
        form.save()
        ticket = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(ticket.status,'split')

    def test_no_comment(self):
        '''form is not valid without a comment'''

        initial = {
            'status1': 'new',
            'ticket_type1': self.ticket.ticket_type,
            'priority1': self.ticket.priority,
            'assigned_to1': self.ticket.assigned_to,
            'description1': self.ticket.description,
            'status2': 'new',
            'ticket_type2': self.ticket.ticket_type,
            'priority2': self.ticket.priority,
            'assigned_to2': self.ticket.assigned_to,
            'description2': self.ticket.description,
            #'comment': 'This is a test',
        }

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertFalse(form.is_valid())

    def test_no_description1(self):
        '''form is not valid without description for the first
        ticket
        '''

        initial = {
            'status1': 'new',
            'ticket_type1': self.ticket.ticket_type,
            'priority1': self.ticket.priority,
            'assigned_to1': self.ticket.assigned_to,
            #'description1': self.ticket.description,
            'status2': 'new',
            'ticket_type2': self.ticket.ticket_type,
            'priority2': self.ticket.priority,
            'assigned_to2': self.ticket.assigned_to,
            'description2': self.ticket.description,
            'comment': 'This is a test',
        }

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertFalse(form.is_valid())


    def test_no_description2(self):
        '''form is not valid without description for the second
        ticket
        '''

        initial = {
            'status1': 'new',
            'ticket_type1': self.ticket.ticket_type,
            'priority1': self.ticket.priority,
            'assigned_to1': self.ticket.assigned_to,
            'description1': self.ticket.description,
            'status2': 'new',
            'ticket_type2': self.ticket.ticket_type,
            'priority2': self.ticket.priority,
            'assigned_to2': self.ticket.assigned_to,
            #'description2': self.ticket.description,
            'comment': 'This is a test',
        }

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertFalse(form.is_valid())


    def test_assigned_to_option(self):
        '''form is valid without assigned_to
        '''

        initial = {
            'status1': 'new',
            'ticket_type1': self.ticket.ticket_type,
            'priority1': self.ticket.priority,
            #'assigned_to1': self.ticket.assigned_to,
            'application1': self.ticket.application.id,
            'description1': self.ticket.description,
            'status2': 'new',
            'ticket_type2': self.ticket.ticket_type,
            'priority2': self.ticket.priority,
            #'assigned_to2': self.ticket.assigned_to,
            'application2': self.ticket.application.id,
            'description2': self.ticket.description,
            'comment': 'This is a test',
        }

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertTrue(form.is_valid())
