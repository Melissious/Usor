from werkzeug._compat import to_unicode
from flask import current_app, request
from itsdangerous import TimedJSONWebSignatureSerializer, \
    SignatureExpired, BadSignature

from .common.flask import APIException
from .models.models import Token


def encode_token(data, reason, expires_in=None):
    t = TimedJSONWebSignatureSerializer(
        current_app.config['SECRET_KEY'], expires_in
    )

    payload = {"reason": reason}
    payload.update(data)
    data = to_unicode(t.dumps(payload))

    Token(data, reason).save()
    return data


def decode_token(token, reason, return_header=None):
    payload = None
    if token:
        t = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY']
        )
        try:
            payload = t.loads(token, return_header)
        except SignatureExpired:
            raise APIException("Expired token.", 401)
        except BadSignature:
            raise APIException("Invalid token.", 401)
        if payload["reason"] != reason:
            raise APIException("Invalid token.", 401)

        data = Token.get(token)
        if data is None:
            raise APIException("Invalid token.", 401)
        if data.has_expired:
            raise APIException("Expired token.", 401)

        if reason in ("reset", "activation"):
            data.expired = True
            data.save()
    return payload


def get_token():
    authorization = request.headers.get("Authorization")
    if authorization:
        prefix, auth_token = authorization.split(":")
        if prefix == "jwt":
            if auth_token and len(auth_token) > 0:
                return auth_token
