from functools import wraps
from flask_login import current_user

from .flask import APIException


def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for role in roles:
                if role not in [role.name for role in current_user.roles]:
                    raise APIException("role required", 403)
                break
            return f(*args, **kwargs)

        return wrapped

    return wrapper


def anonymous_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user is not None and current_user.is_authenticated:
            raise APIException("unauthorised action for authenticate user", 401)
        return f(*args, **kwargs)

    return wrapper
