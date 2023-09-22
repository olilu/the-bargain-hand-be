import re

def valid_uuid(uuid):
    regex = re.compile('^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$', re.I)
    match = regex.match(uuid)
    return bool(match)