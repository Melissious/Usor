from flask import Blueprint, request

from ...common.helpers import time_utcnow
from ...common.email import email_sender
from ...token import encode_token, decode_token
from ...common.decorators import marsh
from ...common.flask import APIException
from ...models.models import Token
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
            token=encode_token(
                {"user_id": str(user.id)}, reason="activation", expires_in=172800
            ),
            username=user.username,
        )
        return user.to_dict(), 201


class Login(AnonymousView):
    decorators = [marsh(UserSchema(only=("login", "password")))]

    def post(self, data):
        user = self.authenticate(data["login"], data["password"])
        token = encode_token({"user_id": str(user.id)}, reason="authentication")
        user.tokens.append(Token.objects(data=token).get())
        user.save()
        return user.to_dict(token)


class LoginVerify(BaseView):
    decorators = [marsh(UserSchema(only=("login", "password")))]

    def post(self, data):
        user = self.authenticate(data["login"], data["password"])
        if user:
            return {"message": True}


class EmailVerify(AnonymousView):
    def get(self, token):
        payload = decode_token(token, reason="activation")
        if payload:
            user = self.is_user(payload["user_id"])
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
            user = self.is_user(data["email"])
            user.email_verify = False
            user.save()
            email_sender(
                recipients=user.email,
                subject="Account activation",
                template="mail/activation",
                token=encode_token(
                    {"user_id": str(user.id)}, reason="activation", expires_in=172800
                ),
                username=user.username,
            )
            return {"message": True}


class PasswordForgot(AnonymousView):
    decorators = [marsh(LoginSchema(only=("login",)))]

    def post(self, data):
        user = self.is_user(data["login"])
        email_sender(
            recipients=user.email,
            subject="Reset Password",
            template="mail/reset",
            token=encode_token(
                {"user_id": str(user.id)}, reason="reset", expires_in=7200
            ),
            username=user.username,
        )
        return {"message": True}


class PasswordReset(AnonymousView):
    decorators = [marsh(UserSchema(only=("new_password", "token")))]

    def post(self, data):
        payload = decode_token(data["token"], reason="reset")
        if payload:
            user = self.is_user(payload["user_id"])
            user.password = data["password"]
            user.update_at = time_utcnow()
            user.save()
            return user.to_dict()
        raise APIException(False, 401)
