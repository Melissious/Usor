from ...schemas.user import RoleSchema
from ...models.user import Role, User
from ...common.flask import APIException
from ...common.helpers import time_utcnow
from ...common.decorators import marsh
from ..views import AdminView

role_descrip = RoleSchema(only=("role", "description"))
login_role = RoleSchema(only=("login", "role"))


class RoleList(AdminView):
    def get(self):
        roles = Role.objects.all()
        return {"roles": [role.to_dict() for role in roles]}


class RoleAdd(AdminView):
    decorators = [marsh(role_descrip)]

    def post(self, data):
        if not self.is_role(data["role"]):
            role = Role(data["role"], data.get("description"))
            role.save()
            return role.to_dict(), 201
        raise APIException("existing role", 409)


class RoleDelete(AdminView):
    decorators = [marsh(role_descrip)]

    def post(self, data):
        role = self.is_role(data["role"])

        users = User.objects.all()
        [user.roles.remove(role) for user in users if role in user.roles]

        role.delete()
        return {"message": True}


class RoleEdit(AdminView):
    decorators = [marsh(role_descrip)]

    def post(self, data):
        role = self.is_role(data["role"])
        if data.get("description"):
            role.description = data["description"]
            role.update_at = time_utcnow()
            role.save()
        return role.to_dict()


class RoleAssignRemove(AdminView):
    decorators = [marsh(login_role)]

    def post(self, data, action):
        role = self.is_role(data["role"])
        user = self.is_user(data["login"])
        if action == "assign":
            user.roles.append(role)
        if action == "remove":
            user.roles.remove(role)
        user.save()
        return user.to_dict(None)
