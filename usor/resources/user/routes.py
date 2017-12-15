from flask import Blueprint

from .views import (
    Logout, AccountInfo, AccountUpdate,
    AccountDelete, PasswordChange, PasswordVerify
)
from ...common.helpers import register_view

user_api = Blueprint("user", __name__, )

register_view(user_api, routes=['/logout'], view_func=Logout.as_view('logout'))
register_view(user_api, routes=['/account/info'], view_func=AccountInfo.as_view('account_info'))
register_view(user_api, routes=['/account/update'], view_func=AccountUpdate.as_view('account_update'))
register_view(user_api, routes=['/account/delete'], view_func=AccountDelete.as_view('account_delete'))
register_view(user_api, routes=['/password/change'], view_func=PasswordChange.as_view('password_change'))
register_view(user_api, routes=['/password/verify'], view_func=PasswordVerify.as_view('password_verify'))
