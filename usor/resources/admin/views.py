from ...schemas.user import signup_schema, login_schema
from ...common.flask import APIException
from ...common.helpers import random_string
from ...models.user import User
from ..views import AdminView


class UserList(AdminView):
    # get a unique user info or all user info
    def get(self, usor_id=None):
        if not usor_id:
            req = User.objects.all()
            users = [user.to_dict() for user in req]
            if users:
                return {"users": users}

        user = User.get_user(usor_id)
        if user:
            return user.to_dict()
        raise APIException("user not found", 404)


class CreateUser(AdminView):
    # create a new user
    def post(self):
        user = self.create_user(signup_schema)
        return user.to_dict(), 201


class UserForceLogout(AdminView):
    # force logout a user
    def post(self):
        user, data = self.is_user(login_schema)
        user.sid = random_string(42, special=True)
        user.save()
        return user.to_dict()


class DeleteUser(AdminView):
    # delete user
    def post(self):
        user, data = self.is_user(login_schema)
        user.delete()
        return {"message": True}


class UserStatus(AdminView):
    # activate or deactivate user account
    def post(self, action):
        user, data = self.is_user(login_schema)
        if action == "activate":
            user.activate = True
        if action == "deactivate":
            user.activate = False
        user.save()
        return {"message": True}


class UserAccess(AdminView):
    # allow or forbid a user access
    def post(self, action):
        user, data = self.is_user(login_schema)
        if action == "allow":
            user.access = True
        if action == "forbid":
            user.access = False
        user.save()
        return {"message": True}
