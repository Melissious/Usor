from flask import Blueprint

from ...common.helpers import register_view

from .views import (
    Signup, Login, LoginVerify, EmailVerify,
    EmailVerifyResend, PasswordForgot, PasswordReset
)

auth_api = Blueprint("auth", __name__, )


register_view(auth_api, routes=['/signup'], view_func=Signup.as_view('signup'))
register_view(auth_api, routes=['/login'], view_func=Login.as_view('login'))
register_view(auth_api, routes=['/login/verify'], view_func=LoginVerify.as_view('login_verify'))
register_view(auth_api, routes=['/email/verify/<token>'], view_func=EmailVerify.as_view('email_verify'))
register_view(auth_api, routes=['/email/verify/resend'], view_func=EmailVerifyResend.as_view('email_verify_resend'))
register_view(auth_api, routes=['/password/forgot'], view_func=PasswordForgot.as_view('password_forgot'))
register_view(auth_api, routes=['/password/reset'], view_func=PasswordReset.as_view('password_reset'))
