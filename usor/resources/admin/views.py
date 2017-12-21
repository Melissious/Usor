from ...common.flask import APIException
from ...common.decorators import marsh
from ...models.models import User
from ...schemas.user import UserSchema
from ..views import AdminView

login_schema = UserSchema(only=("login",))


class UserList(AdminView):
    # get a unique user info or all user info
    def get(self, user_id=None):
        if not user_id:
            req = User.objects.all()
            users = [user.to_dict() for user in req]
            if users:
                return {"users": users}

        user = User.get(user_id)
        if user:
            return user.to_dict()
        raise APIException("User not found.", 404)


class CreateUser(AdminView):
    decorators = [
        marsh(UserSchema(only=("username", "email", "password")))
    ]

    # create a new user
    def post(self, data):
        user = self.create_user(
            data["username"], data["email"], data["password"]
        )
        return user.to_dict(), 201


class UserForceLogout(AdminView):
    decorators = [marsh(login_schema)]

    # force logout a user
    def post(self, data):
        user = self.is_user(data["login"])
        user.save()
        return user.to_dict()


class DeleteUser(AdminView):
    decorators = [marsh(login_schema)]

    # delete user
    def post(self, data):
        user = self.is_user(data["login"])
        user.delete()
        return {"message": True}


class UserStatus(AdminView):
    decorators = [marsh(login_schema)]

    # activate or deactivate user account
    def post(self, data, action):
        user = self.is_user(data["login"])
        if action == "activate":
            user.activate = True
        if action == "deactivate":
            user.activate = False
        user.save()
        return {"message": True}


class UserAccess(AdminView):
    decorators = [marsh(login_schema)]

    # allow or forbid a user access
    def post(self, data, action):
        user = self.is_user(data["login"])
        if action == "allow":
            user.access = True
        if action == "forbid":
            user.access = False
        user.save()
        return {"message": True}
