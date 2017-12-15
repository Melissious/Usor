from flask import Blueprint

from .views import (
    CreateUser, DeleteUser, UserList, UserForceLogout,
    UserStatus, UserAccess
)
from ...common.helpers import register_view

admin_api = Blueprint("admin", __name__,)

register_view(admin_api, routes=['/create'], view_func=CreateUser.as_view('create_user'))
register_view(admin_api, routes=['/delete'], view_func=DeleteUser.as_view('delete_user'))
register_view(admin_api, routes=['/info', '/info/<usor_id>'], view_func=UserList.as_view('user_info'))
register_view(admin_api, routes=['/force-logout'], view_func=UserForceLogout.as_view('force_logout'))
register_view(admin_api, routes=['/status/<action>'], view_func=UserStatus.as_view('status_user'))
register_view(admin_api, routes=['/access/<action>'], view_func=UserAccess.as_view('access_user'))
