from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


def priority_widget(priority, size="xs", type="button"):
    """
    Given a ticket priority and button size, return a colour-coded bootstrap
    button with an appropriate label.

    """

    priority_map = {
        "1": ["danger", "Critical"],
        "2": ["warning", "High"],
        "3": ["success", "Normal"],
        "4": ["info", "Low"],
        "5": ["secondary", "Very Low"],
    }

    attr = priority_map.get(priority)
    if type == "button":
        html = '<button type="button" class="btn btn-{0} btn-{1}">{2}</button>'
        html = html.format(attr[0], size, attr[1])
    else:
        if priority == "2" or priority == "4":
            html = '<span class="badge bg-{} text-dark">{}</span>'
        else:
            html = '<span class="badge bg-{}">{}</span>'
        html = html.format(attr[0], attr[1])
    return html


@register.filter
@stringfilter
def priority_badge(priority):
    """
    Given a ticket priority and badge size, return a colour-coded bootstrap
    badge with an appropriate label.
    """

    html = priority_widget(priority, type="badge")
    return mark_safe(html)


@register.filter
@stringfilter
def priority_btn(priority, size="xs"):
    """
    Given a ticket priority and button size, return a colour-coded bootstrap
    button with an appropriate label.
    """

    html = priority_widget(priority, size, type="button")
    return mark_safe(html)


def status_widget(status, size="xs", type="button"):
    """
    Given a ticket status and button size, return a colour-coded bootstrap
    button with an appropriate label.
    """

    status_map = {
        "new": ["success", "New"],
        "accepted": ["info", "Accepted"],
        "assigned": ["primary", "Assigned"],
        "re-opened": ["warning", "Re-Opened"],
        "closed": ["secondary", "Closed"],
        "duplicate": ["secondary", "Closed - Duplicate"],
        "split": ["secondary", "Closed - Split"],
    }

    attr = status_map.get(status.lower(), ["secondary", status])

    if size == "lg" and status in ("closed", "duplicate", "split"):
        attr[0] = "danger"

    if type == "button":
        html = '<button type="button" class="btn btn-{0} btn-{1}">{2}</button>'
        html = html.format(attr[0], size, attr[1])
    else:
        html = '<span class="badge bg-{}">{}</span>'
        html = html.format(attr[0], attr[1])

    return html


@register.filter
@stringfilter
def status_btn(status, size="xs"):
    """
    Given a ticket status and button size, return a colour-coded bootstrap
    button with an appropriate label.
    """

    html = status_widget(status, size, type="button")
    return mark_safe(html)


@register.filter
@stringfilter
def status_badge(status, size="xs"):
    """
    Given a ticket status and button size, return a colour-coded bootstrap
    badge with an appropriate label.
    """

    html = status_widget(status, size, type="badge")
    return mark_safe(html)


def ticket_type_widget(ticket_type, size="xs", type="button"):
    """given a ticket type and button size, return a colour-coded
    bootstrap button with an appropriate label.
    """

    type_map = {
        "bug": ["danger", "Bug Report"],
        "feature": ["secondary", "Feature Request"],
        "task": ["primary", "Task"],
    }

    attr = type_map.get(ticket_type.lower())
    if type == "button":
        html = '<button type="button" class="btn btn-{0} btn-{1}">{2}</button>'
        html = html.format(attr[0], size, attr[1])
    else:
        html = '<span class="badge bg-{}">{}</span>'
        html = html.format(attr[0], attr[1])
    return html


@register.filter
@stringfilter
def ticket_type_btn(ticket_type, size="xs"):
    """given a ticket type and button size, return a colour-coded
    bootstrap button with an appropriate label.
    """

    html = ticket_type_widget(ticket_type, size, type="button")
    return mark_safe(html)


@register.filter
@stringfilter
def ticket_type_badge(ticket_type, size="xs"):
    """given a ticket type and button size, return a colour-coded
    bootstrap button with an appropriate label.
    """

    html = ticket_type_widget(ticket_type, type="badge")
    return mark_safe(html)


@register.filter
@stringfilter
def classify(ticket_attribute):
    """Given a ticket attribute, return a string representation that could
    be used to to assign a class in an html template.

    """

    classString = ticket_attribute.replace(" ", "-").replace("_", "-").lower()

    return mark_safe(classString)


@register.filter
@stringfilter
def space(string):
    """A simple little template filter to replace underscores with spaces"""
    return mark_safe(string.replace("_", " "))


@register.filter
@stringfilter
def format_action(string):
    """A simple little template filter to return a title case, presence
    tense version of a ticket action

    """

    action_map = {
        "re-opened": "Re-Open",
        "closed": "Close",
        "new": "New",
        "accept": "Accept",
        "comment": "Comment on ",
        "assign": "Assign",
        "re-assign": "Accept And Assign",
        "duplicate": "Duplicate",
        "split": "Split",
    }

    return mark_safe(action_map.get(string, string))


@register.simple_tag(takes_context=True)
def query_transform(context, include_page=False, **kwargs):
    """

    Returns the URL-encoded querystring for the current page,
    updating the params with the key/value pairs passed to the tag.

    E.g: given the querystring ?foo=1&bar=2
    {% query_transform bar=3 %} outputs ?foo=1&bar=3
    {% query_transform foo='baz' %} outputs ?foo=baz&bar=2
    {% query_transform foo='one' bar='two' baz=99 %}
    outputs ?foo=one&bar=two&baz=99

    A RequestContext is required for access to the current querystring.

    from: https://gist.github.com/benbacardi/d6cd0fb8c85e1547c3c60f95f5b2d5e1

    if page is true, we will return the page number tag too, if it is
    false, we want to strip it out and reset our filters to page 1.
    This allows the same template tag to be used in paginators and
    'refinement' widgets.  Without, refinement widgets may point to a
    page that doesn't exist after the new filter has been applied.

    """

    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v

    if query.get("page") and not include_page:
        query.pop("page")
    return query.urlencode()
