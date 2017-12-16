from datetime import datetime

from flask import make_response, jsonify
from flask_login import current_user

from ...common.helpers import random_string, time_utcnow
from ...common.email import email_sender
from ...common.token import encode_token, get_token, decode_token
from ...common.flask import APIException
from ...common.decorators import marsh
from ...schemas.user import UserSchema
from ..views import UserView


class Logout(UserView):
    # logout the current user
    def get(self):
        payload = decode_token(get_token())
        if current_user.sid == payload.get("sid"):
            current_user.sid = random_string(32, special=True)
            current_user.save()

            resp = make_response(jsonify({"message": True}))
            resp.set_cookie("access_token", "")
            return resp
        raise APIException("invalid token", 401)


class AccountInfo(UserView):
    # current user account info
    def get(self):
        token = get_token()
        return current_user.to_dict(token)


class AccountUpdate(UserView):
    decorators = [marsh(UserSchema(only=("username", "email"), partial=True))]

    # update current user info
    def post(self, data):
        token = get_token()
        upd_count = 0
        if data.get("username"):
            current_user.username = data["username"]
            upd_count += 1

        if data.get("email"):
            current_user.email = data["email"]
            current_user.email_verify = False
            email_sender(
                recipients=current_user.email,
                subject="Email address confirmation",
                template="mail/activation",
                token=encode_token({"usor_id": str(current_user.id)}),
                username=current_user.username,
            )
            upd_count += 1

        if upd_count > 0:
            current_user.update_at = datetime.utcnow()
            current_user.save()

        return current_user.to_dict(token)


class AccountDelete(UserView):
    # delete current user account
    def post(self):
        current_user.delete()
        resp = make_response(jsonify({"message": True}))
        resp.set_cookie("access_token", "")
        return resp


class PasswordChange(UserView):
    decorators = [marsh(UserSchema(only=("old_password", "new_password")))]

    # change current user password
    def post(self, data):
        if current_user.check_password(data["old_password"]):
            current_user.password = data["new_password"]
            current_user.update_at = time_utcnow()
            current_user.save()
            return current_user.to_dict(get_token())
        raise APIException("invalid credential", 401)


class PasswordVerify(UserView):
    decorators = [marsh(UserSchema(only=("password",)))]

    # verify current user password
    def post(self, data):
        if current_user.check_password(data["password"]):
            return {"message": True}
        raise APIException(False, 401)
