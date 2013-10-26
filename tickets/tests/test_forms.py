
from datetime import datetime

from django.test import TestCase


from tickets.models import *
from tickets.forms import (TicketForm, CloseTicketForm, CommentForm,
                           SplitTicketForm)
from tickets.tests.factories import *


class TestTicketForm(TestCase):
    '''Test the basic functionality of the ticket form'''
    
    def setUp(self):
        '''one ticket and one user that will be used in these tests'''
        self.user1 = UserFactory()
        self.ticket = TicketFactory()
        
    def test_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = {
            'assigned_to':1,
            'status':'new', 
            'ticket_type':'bug', 
            'description':'this is a test', 
            'priority':3, 
        }
        
        form = TicketForm(data=initial, instance=self.ticket)
        form.is_valid()

        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['assigned_to'], self.user1)         
        self.assertEqual(form.cleaned_data['status'], 'new') 
        self.assertEqual(form.cleaned_data['ticket_type'], 'bug')
        self.assertEqual(form.cleaned_data['description'], 'this is a test') 
        self.assertEqual(form.cleaned_data['priority'], 3)
        

    def test_missing_description(self):
        '''Description is a required field - the form should not be valid
        if description is omitted.
        '''

        initial = {
            'assigned_to':1,
            'status':'new', 
            'ticket_type':'bug', 
            #'description':'this is a test', 
            'priority':3, 
        }
        
        form = TicketForm(data=initial, instance=self.ticket)
        self.assertFalse(form.is_valid())

    def test_missing_status(self):
        '''Status is a required field - the form should not be valid
        if status is omitted.
        '''

        initial = {
            'assigned_to':1,
            #'status':'new', 
            'ticket_type':'bug', 
            'description':'this is a test', 
            'priority':3, 
        }
        
        form = TicketForm(data=initial, instance=self.ticket)
        self.assertFalse(form.is_valid())

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
        
    def test_missing_assinged_to_OK(self):
        '''Assigned to is an optional field, the form should still
        validate without it.
        '''

        initial = {
            #'assigned_to':1,
            'status':'new', 
            'ticket_type':'bug', 
            'description':'this is a test', 
            'priority':3, 
        }
        
        form = TicketForm(data=initial, instance=self.ticket)
        self.assertTrue(form.is_valid())

        #check the data
        self.assertEqual(form.cleaned_data['assigned_to'], None)         
        self.assertEqual(form.cleaned_data['status'], 'new') 
        self.assertEqual(form.cleaned_data['ticket_type'], 'bug')
        self.assertEqual(form.cleaned_data['description'], 'this is a test') 
        self.assertEqual(form.cleaned_data['priority'], 3)
        
    def tearDown(self):
        pass


class TestCommentForm(TestCase):

    def setUp(self):

        self.user = UserFactory()
        self.ticket = TicketFactory(submitted_by=self.user)
        self.comment = FollowUpFactory(ticket=self.ticket)
        
    def test_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = { 'comment':"A valid comment"}
        
        form = CommentForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user)
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')
        self.assertFalse(form.cleaned_data['private'])

    def test_good_data_private(self):
        '''verify that the same data comes out as went in, including
        the private flag

        '''

        initial = { 'comment':"A valid comment",
                    'private':True}
        
        form = CommentForm(data=initial, instance=self.comment,
                           ticket=self.ticket, user=self.user)
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')
        self.assertTrue(form.cleaned_data['private'])

    def test_missing_comment(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''

        initial = { 'comment':None}
        form = CommentForm(data=initial, instance=self.comment,
                                   ticket=self.ticket, user=self.user)
        self.assertFalse(form.is_valid())



class TestCloseTicketForm(TestCase):

    def setUp(self):

        self.user = UserFactory()
        self.comment = FollowUpFactory()
        self.ticket = TicketFactory()

        
    def test_duplicate_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = { 'comment':"A valid comment"}
        form = CloseTicketForm(data=initial, instance=self.comment,
                           action='closed', ticket=self.ticket, user=self.user)
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')

    def test_duplicate_good_ticket(self):
        '''verify that the same data comes out as went in - duplicate
        is checked and a valid ticket number
        '''

        initial = { 'comment':"A valid comment", 'duplicate':True,
                    'same_as_ticket':1}
        
        form = CloseTicketForm(data=initial, instance=self.comment,
                           action='closed', ticket=self.ticket, user=self.user)
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')
        self.assertTrue(form.cleaned_data['duplicate'])
        self.assertEqual(form.cleaned_data['same_as_ticket'], 1)

        
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
        print "form.is_valid() = %s" % form.is_valid()

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
        self.ticket = TicketFactory()
        
    def test_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = {
            'status1':'new',
            'ticket_type1':self.ticket.ticket_type,
            'priority1':self.ticket.priority,
            'assigned_to1':self.ticket.assigned_to,
            'description1':self.ticket.description,
            'status2':'new',
            'ticket_type2':self.ticket.ticket_type,
            'priority2':self.ticket.priority,
            'assigned_to2':self.ticket.assigned_to,
            'description2':self.ticket.description,
            'comment':'This is a test',
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
        print "ticket.get_children() = %s" % ticket.get_children()        
        self.assertEqual(ticket.status,'split')
        

        

    def test_no_comment(self):
        '''form is not valid without a comment'''

        initial = {
            'status1':'new',
            'ticket_type1':self.ticket.ticket_type,
            'priority1':self.ticket.priority,
            'assigned_to1':self.ticket.assigned_to,
            'description1':self.ticket.description,
            'status2':'new',
            'ticket_type2':self.ticket.ticket_type,
            'priority2':self.ticket.priority,
            'assigned_to2':self.ticket.assigned_to,
            'description2':self.ticket.description,
            #'comment':'This is a test',
        } 

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertFalse(form.is_valid())

    def test_no_description1(self):
        '''form is not valid without description for the first
        ticket
        '''

        initial = {
            'status1':'new',
            'ticket_type1':self.ticket.ticket_type,
            'priority1':self.ticket.priority,
            'assigned_to1':self.ticket.assigned_to,
            #'description1':self.ticket.description,
            'status2':'new',
            'ticket_type2':self.ticket.ticket_type,
            'priority2':self.ticket.priority,
            'assigned_to2':self.ticket.assigned_to,
            'description2':self.ticket.description,
            'comment':'This is a test',
        } 

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertFalse(form.is_valid())


    def test_no_description2(self):
        '''form is not valid without description for the second
        ticket
        '''

        initial = {
            'status1':'new',
            'ticket_type1':self.ticket.ticket_type,
            'priority1':self.ticket.priority,
            'assigned_to1':self.ticket.assigned_to,
            'description1':self.ticket.description,
            'status2':'new',
            'ticket_type2':self.ticket.ticket_type,
            'priority2':self.ticket.priority,
            'assigned_to2':self.ticket.assigned_to,
            #'description2':self.ticket.description,
            'comment':'This is a test',
        } 

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertFalse(form.is_valid())
        

    def test_assigned_to_option(self):
        '''form is valid without assigned_to
        '''

        initial = {
            'status1':'new',
            'ticket_type1':self.ticket.ticket_type,
            'priority1':self.ticket.priority,
            #'assigned_to1':self.ticket.assigned_to,
            'description1':self.ticket.description,
            'status2':'new',
            'ticket_type2':self.ticket.ticket_type,
            'priority2':self.ticket.priority,
            #'assigned_to2':self.ticket.assigned_to,
            'description2':self.ticket.description,
            'comment':'This is a test',
        } 

        form = SplitTicketForm(data=initial, user=self.user,
                               original_ticket=self.ticket)
        self.assertTrue(form.is_valid())
        

        
        
        