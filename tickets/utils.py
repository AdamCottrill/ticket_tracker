def is_admin(user):
    """
    return true if the user belongs to the admin group, false otherwise
    """
    if user.groups.filter(name="admin").exists() or user.is_superuser:
        return True
    else:
        return False


def replace_links(text, link_patterns):
    """
    A little function that will replace string patterns in text with
    supplied hyperlinks.  'text' is just a string, most often a field
    in a django or flask model.  link patter is a list of two element
    dictionaries.  Each dictionary must have keys 'pattern' and
    'url'.  'pattern' the regular expression to apply to the text
    while url is the text to be used as its replacement.  Regular
    expression call backs are supported.  See the python documentation
    for re.sub for more details.

    Note: The function does not make any attempt to validate the link or
    the regex pattern.

    """

    import re

    for pattern in link_patterns:
        regex = re.compile(pattern.get("pattern"), re.IGNORECASE)
        text = re.sub(regex, pattern["url"], text)
    return text
