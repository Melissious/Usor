from functools import wraps

from flask import request
from marshmallow import Schema, ValidationError
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


def marsh(schema):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if isinstance(schema, Schema):
                schema.strict = True
                try:
                    data, error = schema.load(request.get_json())
                except ValidationError as err:
                    raise APIException(err.messages, 401)
                return f(data, *args, **kwargs)
            raise Exception("Invalid marshmallow schema instance.")
        return wrapped

    return wrapper
