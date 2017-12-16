import pyotp
from werkzeug._compat import to_unicode
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature
from flask import current_app, request
from .flask import APIException


def encode_token(data, expires_in=31104000):
    totp = pyotp.TOTP(current_app.config['TOTP_KEY'])

    t = TimedJSONWebSignatureSerializer(
        current_app.config['SECRET_KEY'], expires_in
    )

    payload = {"ott": totp.now()}
    payload.update(data)
    token = t.dumps(payload)
    return to_unicode(token)


def decode_token(token, one_time_token=False, return_header=None):
    payload = None
    if token is not None:
        totp = pyotp.TOTP(current_app.config['TOTP_KEY'])

        t = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY']
        )
        try:
            payload = t.loads(token, return_header)
        except SignatureExpired:
            raise APIException("expired token", 401)
        except BadSignature:
            raise APIException("invalid token", 401)
        if one_time_token:
            print(payload)
            if not totp.verify(payload["ott"]):
                raise APIException("token already used", 401)
    return payload


def get_token():
    auth_token = request.cookies.get("access_token")
    if auth_token:
        return auth_token

    authorization = request.headers.get("Authorization")
    if authorization:
        prefix, auth_token = authorization.split(":")
        if prefix == "jwt":
            if auth_token and len(auth_token) > 0:
                return auth_token
