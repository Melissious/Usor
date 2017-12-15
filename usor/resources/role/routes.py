from flask import Blueprint

from .views import RoleList, RoleAdd, RoleDelete, RoleEdit, RoleAssignRemove
from ...common.helpers import register_view

role_api = Blueprint('role', __name__)


register_view(role_api, routes=['/list'], view_func=RoleList.as_view('role_list'))
register_view(role_api, routes=['/add'], view_func=RoleAdd.as_view('role_add'))
register_view(role_api, routes=['/delete'], view_func=RoleDelete.as_view('role_delete'))
register_view(role_api, routes=['/edit'], view_func=RoleEdit.as_view('role_edit'))
register_view(role_api, routes=['/user/<action>'], view_func=RoleAssignRemove.as_view('role_assign_remove'))
