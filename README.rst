=====
Ticket Tracker
=====

TicketTracker is a simple django application designed to keep track
of tickets representing bug reports or feature requests.  Basic list
views including all tickets, open tickets, closed tickets, bug
reports, feature requests, and 'My Tickets' have been implemented,
and could be easily augmented or extended.

Users can open and update their own tickets, as well as comment on or
vote for existing tickets opened by other users.

Links to other tickets are supported in the ticket description or
comments using the following convention 'ticket: N' where N is the
ticket number.  Administrators can close tickets, mark them as
duplicate (including a link to duplicate), or split tickets that
involve more than one bug or feature.  Additionally, administrators
can re-open tickets if necessary.

While TicketTracker could be used as a standalone project, it is most
often used as an add-in application for larger projects.  I regularly
use a version of ticket tracker in my own applications during
development and integrate another version in the final deployed
project to provide users with a means of providing feedback and
influencing the future development of the project.


TicketTracker was developed by extending and augmenting a django
project that was described in this screencast tutorial:
[[http://net.tutsplus.com/tutorials/python-tutorials/diving-into-django/]]

Adam Cottrill
Wed Jul 09 2014
Tues Jul 23 2019



Detailed documentation is in the "docs" directory.

Quick start
-----------

0. > pip install tickets.zip

0.5 install associated requirements: django-taggit, django_filter,
  markdown2, and django-crispy-forms.

1. Add "tickets" and assocaited requirements to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...
        'crispy_forms',
        'taggit',
        'tickets',
    ]

2. Include the common URLconf in your project urls.py like this:

    path('tickets/', include(('tickets.urls', 'tickets'), 'tickets')),

3. Run `python manage.py migrate` to create the common models in your database.

4. Visit http://127.0.0.1:8000/


For Developers
--------------------------

Here are the steps required to install the TicketTracker repository
and create an associated virtual environment on you computer.

1. Clone the git repository:

   > git clone https://github.com/AdamCottrill/ticket_tracker.git

2. Create a virtual environment:

   > python -m venv env

3. Install the required dependencies in the virtual env you just created:

   (venv)> pip install -r ./requirements/local.txt

4. Run migrations to create database and update all of the migrations
   associated with installed apps:

   (venv)> python manage.py migrate

   If you are going to use an existing copy of the ticket tracker data
   base with exsisting tickets, be sure to place a copy of it here:
   ~/db/tickettracker.db before running the migrate command.

5. Verify that all of the requirements have been installed and that
   everything is where it should be:

   (venv)> python manage.py check

6. Run the tests with pytest.

   I typically select a single models file to verify that the testing
   environment is set up correctly to limit the length of the error
   report if something goes wrong:

   (venv)> pytest tickets\tests\test_models.py

   If all of the tests pass, go ahead and run the whole test suite:

   (venv)> pytest

7. Start the developement server:

   (venv)> python manage.py runserver

   The application should be available at http://127.0.0.1:8000


Rebuilding the Distributable App.
---------------------------------

Ticket Tracker was built as a standard applicaiton can be rebuilt for
distrubition following the instructions found here:

https://docs.djangoproject.com/en/2.2/intro/reusable-apps/

With the a virtualenv active, and from within the
~/tickettracker directory, simply run:

(venv)> python setup.py sdist

The package will be placed in the ~/dist folder.  To install the
application in an existing Django project run the command:

(venv)> pip install tickets.zip

To update an existing application issue the command:

(venv)> pip install --upgrade tickets.zip


Running the tests
-----------------

Ticket Tracker contains a number of unit tests that verify that the
application works as expected and that any regregressions are caught
early. The package uses pytest to run all of the tests, which can be
run by issuing the command:

(venv)> pytest

After the tests have completed, coverage reports can be found here:

~/htmlcov
