from ...schemas.user import user_role_schema
from ...models.user import Role, User
from ...schemas.user import role_schema
from ...common.flask import APIException
from ...common.helpers import time_utcnow
from ..views import AdminView


class RoleList(AdminView):
    def get(self):
        roles = Role.objects.all()
        return {"roles": [role.to_dict() for role in roles]}


class RoleAdd(AdminView):
    def post(self):
        data = self.get_request_data(role_schema)
        if not Role.get_role(data["role"]):
            role = Role(data["role"], data.get("description"))
            role.save()
            return role.to_dict(), 201
        raise APIException("existing role", 409)


class RoleDelete(AdminView):
    def post(self):
        role, data = self.is_role(role_schema)
        role.delete()
        return {"message": True}


class RoleEdit(AdminView):
    def post(self):
        role, data = self.is_role(role_schema)
        if data.get("description"):
            role.description = data["description"]
            role.update_at = time_utcnow()
            role.save()
        return role.to_dict()


class RoleAssignRemove(AdminView):
    def post(self, action):
        role, data = self.is_role(user_role_schema)
        user = User.get_user(data["login"])
        if action == "assign":
            user.roles.append(role)
        if action == "remove":
            user.roles.remove(role)
        user.save()
        return user.to_dict(None)
