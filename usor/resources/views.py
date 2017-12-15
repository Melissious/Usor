from flask import request
from flask.views import MethodView
from flask_login import login_required

from ..models.user import User, Role
from ..common.flask import APIException
from ..common.helpers import random_string
from ..common.decorators import roles_required, anonymous_required


class BaseView(MethodView):
    def get_request_data(self, schema):
        data, errors = schema.load(request.get_json())
        if errors:
            raise APIException(errors, 422)
        return data

    def is_user(self, schema):
        data = self.get_request_data(schema)
        user = User.get_user(data["login"])
        if user:
            return user, data
        raise APIException("user not found", 404)

    def authenticate_user(self, schema):
        data = self.get_request_data(schema)
        user = User.authenticate(data["login"], data["password"])
        if user:
            return user
        raise APIException("invalid credential", 401)

    def is_role(self, schema):
        data = self.get_request_data(schema)
        role = Role.objects(name=data["role"]).get()
        if role:
            return role, data
        raise APIException("role not found", 404)

    def create_user(self, schema):
        data = self.get_request_data(schema)
        user = User(data["username"], data["email"], data["password"])
        user.sid = random_string(32, special=True)
        user.roles.append(Role.objects(name="user").get())
        return user.save()


class AdminView(BaseView):
    decorators = [login_required, roles_required("admin")]


class UserView(BaseView):
    decorators = [login_required]


class AnonymousView(BaseView):
    decorators = [anonymous_required]
