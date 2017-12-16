from flask.views import MethodView
from flask_login import login_required

from ..models.user import User, Role
from ..common.flask import APIException
from ..common.helpers import random_string
from ..common.decorators import roles_required, anonymous_required


class BaseView(MethodView):

    def is_user(self, id):
        user = User.get_user(id)
        if user:
            return user
        raise APIException("user not found.", 404)

    def is_role(self, id):
        role = Role.get_role(id)
        if role:
            return role
        raise APIException("role not found.", 404)

    def authenticate(self, login, password):
        user = User.authenticate(login, password)
        if user:
            return user
        raise APIException("invalid credential.", 401)

    def create_user(self, username, email, password):
        user = User(username, email, password)
        user.sid = random_string(32, special=True)
        user.roles.append(Role.objects(name="user").get())
        return user.save()


class AdminView(BaseView):
    decorators = [login_required, roles_required("admin")]


class UserView(BaseView):
    decorators = [login_required]


class AnonymousView(BaseView):
    decorators = [anonymous_required]
