
from datetime import datetime

from django.test import TestCase

#there aren't many forms in this project, but they should be tested

#forms to test:
# TicketForm
#  - new ticket
#  - update ticket
#     - admin and owner only
# SplitTicketForm **


# CommentForm *
# user
# close
# close duplicate
# re-open

#  * - login required


from tickets.models import *
from tickets.forms import TicketForm, CommentForm
from tickets.tests.factories import *


class TestTicketForm(TestCase):

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()        
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

        self.comment = FollowUpFactory()
        self.ticket = TicketFactory()
        
    def test_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = { 'comment':"A valid comment"}
        
        form = CommentForm(data=initial, instance=self.comment)
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')

    def test_missing_comment(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''

        initial = { 'comment':None}
        
        form = CommentForm(data=initial, instance=self.comment)
        self.assertFalse(form.is_valid())


    def test_duplicate_good_data(self):
        '''verify that the same data comes out as went in'''

        initial = { 'comment':"A valid comment"}
        
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
        self.assertTrue(form.is_valid())
        #check the data
        self.assertEqual(form.cleaned_data['comment'],
                         'A valid comment')

    def test_duplicate_good_ticket(self):
        '''verify that the same data comes out as went in'''

        initial = { 'comment':"A valid comment", 'duplicate':True,
                    'same_as_ticket':1}
        
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
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
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
        self.assertFalse(form.is_valid())

        
    def test_duplicate_missing_ticket(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''

        initial = { 'comment':'This is a valid comment',
                    'duplicate':True}        
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
        print "form.is_valid() = %s" % form.is_valid()

        self.assertFalse(form.is_valid())
        
    def test_duplicate_bad_ticket(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''
        
        initial = { 'comment':'This is a valid comment',
                    'duplicate':True, 'same_as_ticket':99}
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
        self.assertFalse(form.is_valid())


    def test_duplicate_non_numeric_ticket(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''
        
        initial = { 'comment':'This is a valid comment',
                    'duplicate':True, 'same_as_ticket':'abc'}
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
        self.assertFalse(form.is_valid())


        
    def test_duplicate_missing_check(self):
        '''comment is a required field, verify that the form will not
        validate without it.
        '''

        initial = { 'comment':'This is a valid comment', 'duplicate':False,
                    'same_as_ticket':1}
        
        form = CommentForm(data=initial, instance=self.comment,
                           action='closed')
        self.assertFalse(form.is_valid())

        

    def tearDown(self):
        pass
        