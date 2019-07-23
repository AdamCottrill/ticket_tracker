"""The tests in this file verify that the views associated with tags
work as expected.  Tests include:

- tags in detail view
- tags in ticket form


"""

from django.urls import reverse
from django.test import TestCase

from tickets.tests.factories import UserFactory, TicketFactory


class ProjectTaggingTestCase(TestCase):
    """Verify that the projects can be tagged with keywords in the
    project form."""

    def setUp(self):
        """ """

        """create a user, some languages and three snippets"""
        self.user1 = UserFactory(username="gcostanza")

        self.ticket1 = TicketFactory(submitted_by=self.user1)
        self.ticket2 = TicketFactory(submitted_by=self.user1)
        self.ticket3 = TicketFactory(submitted_by=self.user1)

    def tearDown(self):
        """ """

        self.ticket2.delete()
        self.ticket1.delete()
        self.user1.delete()

    def test_tags_in_snippet_details_view(self):
        """verify that the tags associated with a snippet appear on
        its details (and not on others)"""

        # assign some tags to project1
        tags = ["red", "blue", "green", "yellow"]
        tags.sort()
        for tag in tags:
            self.ticket1.tags.add(tag)

        # =======================
        # verify that the tags are associated with that project
        tags_back = self.ticket1.tags.all().order_by("name")
        self.assertQuerysetEqual(tags_back, tags, lambda a: str(a.name))
        self.assertEqual(tags_back.count(), len(tags))

        # verify that the tag appears as a hyperlink on the details
        # page for this project:
        response = self.client.get(
            reverse("tickets:ticket_detail", args=(self.ticket1.pk,)), user=self.user1
        )
        self.assertEqual(response.status_code, 200)

        linkstring_base = '<a href="{}">{}</a>'
        for tag in tags:
            tag_url = reverse("tickets:tickets_tagged_with", args=(tag,))
            linkstring = linkstring_base.format(tag_url, tag)
            self.assertContains(response, linkstring)

        # =======================
        # verify that the tags are NOT associated with project2
        response = self.client.get(
            reverse("tickets:ticket_detail", args=(self.ticket2.pk,)), user=self.user1
        )
        self.assertEqual(response.status_code, 200)

        linkstring_base = '<a href="{}">{}</a>'
        for tag in tags:
            tag_url = reverse("tickets:tickets_tagged_with", args=(tag,))
            linkstring = linkstring_base.format(tag_url, tag)
            self.assertNotContains(response, linkstring)

    def test_tags_ticket_list_view(self):
        """This test verifies that the url for 'tickets_tagged_with' returns
        just the tickets with that tag and includes an informative
        heading.  Tags that do not have the specified tag, should not
        be included in the response.
        """

        # tickets 1 and 2 will be tagged, ticket three is not:
        tags = ["red", "blue"]
        tags.sort()
        for tag in tags:
            self.ticket1.tags.add(tag)
            self.ticket2.tags.add(tag)

        # =======================
        # verify that the tags are associated with that ticket
        tags_back = self.ticket1.tags.all().order_by("name")
        self.assertQuerysetEqual(tags_back, tags, lambda a: str(a.name))

        tags_back = self.ticket2.tags.all().order_by("name")
        self.assertQuerysetEqual(tags_back, tags, lambda a: str(a.name))

        # load the page associated with tag 1 and verify that it
        # contains records for tickett 1 and 2 (as hyperlinks), but
        # not ticket 3
        response = self.client.get(
            reverse("tickets:tickets_tagged_with", args=(tags[0],)), user=self.user1
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tickets\ticket_list.html")

        msg = "Tickets Tagged with '{}'".format(tags[0])
        self.assertContains(response, msg)

        link_base = '<td><a href="{}">{}</a></td>'

        ticket_list = [self.ticket1, self.ticket2, self.ticket3]

        for ticket in ticket_list[:2]:
            url = link_base.format(ticket.get_absolute_url(), ticket.id)
            self.assertContains(response, url, html=True)

        url = link_base.format(self.ticket3.get_absolute_url(), self.ticket3.id)
        self.assertNotContains(response, url, html=True)

        # ====================
        # navigate to the whole ticket list and verify that it contain
        # records for all three tickets
        response = self.client.get(reverse("tickets:ticket_list"), user=self.user1)
        self.assertEqual(response.status_code, 200)

        for ticket in ticket_list:
            url = link_base.format(ticket.get_absolute_url(), ticket.id)
            self.assertContains(response, url, html=True)
