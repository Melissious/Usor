import re
from random import SystemRandom
from string import ascii_lowercase, digits, ascii_uppercase

import unidecode
import pytz

from datetime import datetime
from flask_login.utils import _get_remote_addr
from werkzeug._compat import to_unicode, text_type

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    text = unidecode.unidecode(text)
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return text_type(delim.join(result))


def get_remote_addr():
    return to_unicode(_get_remote_addr())


def register_view(bp_or_app, routes, view_func, *args, **kwargs):
    for route in routes:
        bp_or_app.add_url_rule(route, view_func=view_func, *args, **kwargs)


def time_utcnow():
    return datetime.now(pytz.UTC)


def random_string(length=12, special=None):
    collection = ascii_lowercase + digits + ascii_uppercase
    if special:
        collection += r"""!#$%&-.?@_"""
    return "".join(
        SystemRandom().choice(collection) for _ in range(length))
