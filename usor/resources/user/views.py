from datetime import datetime

from flask import request, make_response, jsonify
from flask_login import current_user

from ...common.helpers import random_string, time_utcnow
from ...common.email import email_sender
from ...common.token import encode_token, get_token, decode_token
from ...common.flask import APIException
from ...schemas.user import update_schema, pwd_schema, update_pwd_schema
from ..views import UserView


class Logout(UserView):
    # logout the current user
    """Logout endpoint.
    ---
    get:
        description: logout current user
        responses:
            200:
                description: A pet to be returned
                schema: UserSchema
    """
    def get(self):
        payload = decode_token(get_token(request))
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
        token = get_token(request)
        return current_user.to_dict(token)


class AccountUpdate(UserView):
    # update current user info
    def post(self):
        token = get_token(request)
        data = self.get_request_data(update_schema)

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
    # change current user password
    def post(self):
        data = self.get_request_data(update_pwd_schema)
        if current_user.check_password(data["old_password"]):
            current_user.password = data["new_password"]
            current_user.update_at = time_utcnow()
            current_user.save()
            return current_user.to_dict(get_token(request))
        raise APIException("invalid credential", 401)


class PasswordVerify(UserView):
    # verify current user password
    def post(self):
        data = self.get_request_data(pwd_schema)
        if current_user.check_password(data["password"]):
            return {"message": True}
        raise APIException(False, 401)
