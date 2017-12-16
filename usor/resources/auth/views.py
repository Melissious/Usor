from flask import Blueprint, request, current_app, make_response

from ...common.helpers import time_utcnow, random_string
from ...common.email import email_sender
from ...common.token import encode_token, decode_token
from ...common.decorators import marsh
from ...common.flask import APIException
from ...models.user import User
from ...schemas.user import UserSchema, LoginSchema
from ..views import AnonymousView, BaseView

auth_api = Blueprint("auth", __name__, )


class Signup(AnonymousView):
    decorators = [marsh(UserSchema(only=("username", "email", "password")))]

    def post(self, data):
        user = self.create_user(data["username"], data["email"], data["password"])
        email_sender(
            recipients=user.email,
            subject="Email address confirmation",
            template="mail/activation",
            token=encode_token({"usor_id": str(user.id)}),
            username=user.username,
        )
        return user.to_dict(), 201


class Login(AnonymousView):
    decorators = [marsh(UserSchema(only=("login", "password")))]

    def post(self, data):
        user = self.authenticate(data["login"], data["password"])
        if not current_app.config.get("APP_MULTI_SESSION"):
            user.sid = random_string(32, special=True)
            user.save()

        token = encode_token({"usor_id": str(user.id), "sid": user.sid})
        resp = make_response(user.to_dict(token))
        resp.set_cookie(
            "access_token", token,
            max_age=None, expires=None,
            domain=None, httponly=True
        )
        return resp


class LoginVerify(BaseView):
    decorators = [marsh(UserSchema(only=("login", "password")))]

    def post(self, data):
        user = self.authenticate(data["login"], data["password"])
        if user:
            return {"message": True}


class EmailVerify(AnonymousView):
    def get(self, token):
        payload = decode_token(token, one_time_token=True)
        if payload:
            user = User.get_user(payload["usor_id"])
            if user:
                user.email_verify = True
                user.update_at = time_utcnow()
                user.save()
                return {"message": True}
        return {}, 204


class EmailVerifyResend(AnonymousView):
    def post(self):
        data = request.get_json()
        if "@" in data.get("email"):
            user = User.get_user(data["email"])
            if user:
                user.email_verify = False
                user.save()
                email_sender(
                    recipients=user.email,
                    subject="Account activation",
                    template="mail/activation",
                    token=encode_token({"usor_id": str(user.id)}),
                    username=user.username,
                )
                return {"message": True}
        raise APIException("user not found", 404)


class PasswordForgot(AnonymousView):
    decorators = [marsh(LoginSchema(only=("login",)))]

    def post(self, data):
        user = self.is_user(data["login"])
        email_sender(
            recipients=user.email,
            subject="Reset Password",
            template="mail/reset",
            token=encode_token({"usor_id": str(user.id)}),
            username=user.username,
        )
        return {"message": True}


class PasswordReset(AnonymousView):
    decorators = [marsh(UserSchema(only=("new_password", "token")))]

    def post(self, data):
        payload = decode_token(data["token"], one_time_token=True)
        if payload:
            user = User.get_user(payload["usor_id"])
            if user:
                user.password = data["password"]
                user.update_at = time_utcnow()
                user.save()
                return user.to_dict()
        raise APIException(False, 401)
